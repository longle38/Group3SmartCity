import redis
import json

class RedisTrafficManager:
    def __init__(self):
        self.redis = redis.Redis(connection_pool=redis.ConnectionPool(host='localhost', port=6379, db=0))

    # ===== OPERATION 1: Write-Through Update =====
    def update_signal_state(self, intersection_id, position, state):
        """
        Write-through pattern: Update Redis cache AND persist to backend storage.
        Ensures data consistency by writing to both systems synchronously.
        
        Args:
            intersection_id: ID of the traffic signal intersection
            position: Signal position (e.g., 'northbound', 'southbound')
            state: Signal state ('green', 'yellow', 'red', etc.)
        """
        key = f"signal:{intersection_id}:{position}:state"
        
        # Step 1: Write to Redis cache with 5-minute TTL
        self.redis.setex(key, 300, state)
        
        # Step 2: Persist to backend (write-through to database)
        # In production, this would write to PostgreSQL
        self._persist_signal_to_database(intersection_id, position, state)
        
        return True

    def _persist_signal_to_database(self, intersection_id, position, state):
        """Mock backend persistence layer."""
        # In production: execute SQL INSERT/UPDATE on PostgreSQL
        # Example: UPDATE traffic_signals SET state = state WHERE intersection_id = ? AND position = ?
        print(f"[DB] Persisted signal - Intersection: {intersection_id}, Position: {position}, State: {state}")

    # ===== OPERATION 2: Sorted-Set Ranking Query =====
    def get_top_congested(self, limit=10):
        """
        Query top congested intersections from sorted set with scores.
        Sorted set pattern with congestion index as score (0-100).
        
        Args:
            limit: Number of top results to return
            
        Returns:
            List of tuples: [(intersection_id, congestion_score), ...]
        """
        results = self.redis.zrevrange(
            "congestion:rankings",
            0,
            limit - 1,
            withscores=True
        )
        # Convert bytes to strings for cleaner output
        return [(item[0].decode() if isinstance(item[0], bytes) else item[0], 
                 item[1]) for item in results]

    def update_congestion_ranking(self, intersection_id, congestion_index):
        """
        Update congestion index for an intersection in the sorted set.
        Called by traffic analysis engine every 30 seconds.
        
        Args:
            intersection_id: ID of the intersection
            congestion_index: Numeric score 0-100
        """
        self.redis.zadd(
            "congestion:rankings",
            {f"intersection:{intersection_id}": congestion_index}
        )

    # ===== OPERATION 3: Pub/Sub Publish =====
    def publish_alert(self, channel, message):
        """
        Pub/Sub publish pattern: Broadcast traffic alert to all subscribers.
        Subscribers (mobile app, connected vehicles) receive real-time notifications.
        
        Args:
            channel: Alert channel (e.g., 'north_quad', 'downtown', 'highway_95')
            message: Dict with alert_type, message, severity_level
            
        Returns:
            Number of subscribers that received the message
        """
        channel_key = f"alerts:broadcast:{channel}"
        subscriber_count = self.redis.publish(
            channel_key,
            json.dumps(message)
        )
        return subscriber_count

    def subscribe_to_alerts(self, channel):
        """
        Subscribe to traffic alerts on a specific channel.
        Used by mobile app backend or connected vehicle units.
        
        Args:
            channel: Alert channel to subscribe to
            
        Returns:
            PubSub object for listening to messages
        """
        pubsub = self.redis.pubsub()
        pubsub.subscribe(f"alerts:broadcast:{channel}")
        return pubsub

    # ===== OPERATION 4: Cache-Aside Read =====
    def get_intersection_metrics(self, intersection_id):
        """
        Cache-aside (lazy loading) pattern: Read from cache first,
        if miss, fetch from source and populate cache.
        
        Args:
            intersection_id: ID of the intersection
            
        Returns:
            Dict with metrics: throughput, occupancy, avg_wait_time, pedestrian_count
        """
        cache_key = f"metrics:{intersection_id}"
        
        # Step 1: Try to read from cache
        cached_metrics = self.redis.hgetall(cache_key)
        if cached_metrics:
            # Cache hit: return parsed metrics
            return {k.decode(): v.decode() if isinstance(v, bytes) else v 
                    for k, v in cached_metrics.items()}
        
        # Step 2: Cache miss - fetch from source (sensors/processors)
        metrics = self._fetch_metrics_from_source(intersection_id)
        
        # Step 3: Populate cache with 10-minute TTL
        if metrics:
            self.redis.hset(cache_key, mapping=metrics)
            self.redis.expire(cache_key, 600)  # 10-minute TTL
        
        return metrics

    def _fetch_metrics_from_source(self, intersection_id):
        """Mock source layer (edge sensors, computer vision processors)."""
        # In production: query PostgreSQL or fetch from IoT sensors
        print(f"[SOURCE] Fetching metrics for intersection {intersection_id}")
        return {
            "throughput": "45",
            "occupancy": "0.82",
            "avg_wait_time": "12",
            "pedestrian_count": "8"
        }