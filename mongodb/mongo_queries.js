db = db.getSiblingDB("traffic_management");

const WINDOW_START = ISODate("2026-04-01T00:00:00Z");
const WINDOW_END = ISODate("2026-05-01T00:00:00Z");

// -----------------------------------------------------------------------------
// Query #1: Hourly average vehicle counts by intersection
// Business Question: For operations planning, how does typical hourly volume
//   vary by intersection in the analysis month?
// Collections Used: traffic_flow_events
// Pipeline Stages: $match, $group ($dateTrunc hour), $sort, $limit
//
db.traffic_flow_events
    .aggregate([
        {
            $match: {
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
            },
        },
        {
            $group: {
                _id: {
                    intersection_id: "$intersection_id",
                    hour_bucket: {
                        $dateTrunc: { date: "$timestamp", unit: "hour", timezone: "UTC" },
                    },
                },
                avg_vehicle_count: { $avg: "$vehicle_count" },
                readings: { $sum: 1 },
            },
        },
        { $sort: { "_id.intersection_id": 1, "_id.hour_bucket": 1 } },
        { $limit: 24 },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: One document per (intersection_id, UTC hour bucket) with
//   avg_vehicle_count (double) and readings (count of events in that bucket).
// Sample Results: First buckets for low-numbered intersections with ~1 event/hour in seed.

// -----------------------------------------------------------------------------
// Query #2: Top 5 intersections by high-congestion event frequency
// Business Question: Which intersections logged the most high/severe congestion
//   events during the analysis period?
// Collections Used: traffic_flow_events
// Pipeline Stages: $match, $group, $sort, $limit
//
db.traffic_flow_events
    .aggregate([
        {
            $match: {
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
                congestion_level: { $in: ["high", "severe"] },
            },
        },
        {
            $group: {
                _id: "$intersection_id",
                stress_events: { $sum: 1 },
            },
        },
        { $sort: { stress_events: -1 } },
        { $limit: 5 },
        {
            $project: {
                _id: 0,
                intersection_id: "$_id",
                stress_events: 1,
            },
        },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: Up to 5 rows: intersection_id (int), stress_events (int).
// Sample Results: intersection_id values from 1–56; counts depend on seed mix.

// -----------------------------------------------------------------------------
// Query #3: Sensor reading counts by sensor type and calendar day
// Business Question: How many readings did we ingest per sensor family per day?
// Collections Used: sensor_readings
// Pipeline Stages: $match, $group ($dateTrunc day), $sort
//
db.sensor_readings
    .aggregate([
        {
            $match: {
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
            },
        },
        {
            $group: {
                _id: {
                    sensor_type: "$sensor_type",
                    day: {
                        $dateTrunc: { date: "$timestamp", unit: "day", timezone: "UTC" },
                    },
                },
                reading_count: { $sum: 1 },
            },
        },
        { $sort: { "_id.sensor_type": 1, "_id.day": 1 } },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: One row per (sensor_type, UTC day) with reading_count.
// Sample Results: camera / radar / lidar rows with counts from seeded 220 docs.

// -----------------------------------------------------------------------------
// Query #4: Average traffic speed by intersection (month window)
// Business Question: Which intersections show the lowest average measured
//   speeds across all flow events in the month?
// Collections Used: traffic_flow_events
// Pipeline Stages: $match, $group, $sort, $limit
//
db.traffic_flow_events
    .aggregate([
        {
            $match: {
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
            },
        },
        {
            $group: {
                _id: "$intersection_id",
                avg_speed_kmh: { $avg: "$avg_speed" },
                event_count: { $sum: 1 },
            },
        },
        { $sort: { avg_speed_kmh: 1 } },
        { $limit: 10 },
        {
            $project: {
                _id: 0,
                intersection_id: "$_id",
                avg_speed_kmh: { $round: ["$avg_speed_kmh", 2] },
                event_count: 1,
            },
        },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: 10 “slowest average speed” intersections with rounded mean.
// Sample Results: intersection_id, avg_speed_kmh ~ tens of km/h, event_count ~ 9–10 for grid seed.

// -----------------------------------------------------------------------------
// Query #5: Lane-level demand after unwinding lane_distribution (ARRAY)
// Business Question: After exploding nested lanes, what is the average vehicle
//   count per lane index per intersection?
// Collections Used: traffic_flow_events
// Pipeline Stages: $match, $unwind, $group, $sort, $limit
//
db.traffic_flow_events
    .aggregate([
        {
            $match: {
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
            },
        },
        { $unwind: "$lane_distribution" },
        {
            $group: {
                _id: {
                    intersection_id: "$intersection_id",
                    lane: "$lane_distribution.lane",
                },
                avg_lane_vehicles: { $avg: "$lane_distribution.count" },
                samples: { $sum: 1 },
            },
        },
        { $sort: { "_id.intersection_id": 1, "_id.lane": 1 } },
        { $limit: 20 },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: Per (intersection_id, lane number), avg lane vehicle count.
// Sample Results: lane 1–5, avg_lane_vehicles in tens.

// -----------------------------------------------------------------------------
// Query #6: Camera detection mix — unwind detection_results (ARRAY)
// Business Question: Across camera sensors, what total detections and average
//   confidence do we see per vehicle class?
// Collections Used: sensor_readings
// Pipeline Stages: $match, $unwind, $group, $sort
//
db.sensor_readings
    .aggregate([
        {
            $match: {
                sensor_type: "camera",
                timestamp: { $gte: WINDOW_START, $lt: WINDOW_END },
            },
        },
        { $unwind: "$detection_results" },
        {
            $group: {
                _id: "$detection_results.type",
                total_detections: { $sum: "$detection_results.count" },
                avg_confidence: { $avg: "$detection_results.confidence" },
                observations: { $sum: 1 },
            },
        },
        { $sort: { total_detections: -1 } },
        {
            $project: {
                vehicle_class: "$_id",
                total_detections: 1,
                avg_confidence: { $round: ["$avg_confidence", 3] },
                observations: 1,
                _id: 0,
            },
        },
    ])
    .forEach((doc) => printjson(doc));

// Expected Output: One row per detection type (car, truck, …) with aggregates.
// Sample Results: e.g. car with larger total_detections than truck from seed.

print("mongo_queries.js: finished running 6 query blocks.");
