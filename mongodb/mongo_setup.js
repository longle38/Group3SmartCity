// Create database and collections
use traffic_management;

// Create collection with validation
db.createCollection("traffic_flow_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["intersection_id", "timestamp", "vehicle_count"],
      properties: {
        intersection_id: { bsonType: "int" },
        timestamp: { bsonType: "date" },
        vehicle_count: { bsonType: "int", minimum: 0 }
      }
    }
  }
});

// Create indexes
db.traffic_flow_events.createIndex(
  { intersection_id: 1, timestamp: -1 }
);

db.traffic_flow_events.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 7776000 }  // 90 days
);