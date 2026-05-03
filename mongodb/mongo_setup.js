// Create database and collections
use traffic_management;

[
  "traffic_flow_events",
  "sensor_readings",
  "incident_reports",
  "weather_station_readings",
].forEach((n) => {
  db.getCollection(n).drop();
});

// Create collection with validation
db.createCollection("traffic_flow_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "intersection_id",
        "timestamp",
        "vehicle_count",
        "avg_speed",
        "congestion_level",
        "lane_distribution",
      ],
      properties: {
        intersection_id: { bsonType: "int", minimum: 1 },
        timestamp: { bsonType: "date" },
        vehicle_count: { bsonType: "int", minimum: 0 },
        avg_speed: { bsonType: ["double", "int"] },
        congestion_level: {
          bsonType: "string",
          enum: ["low", "moderate", "high", "severe"],
        },
        lane_distribution: {
          bsonType: "array",
          minItems: 1,
          maxItems: 6,
          items: {
            bsonType: "object",
            required: ["lane", "count", "avg_speed"],
            properties: {
              lane: { bsonType: "int", minimum: 1, maximum: 6 },
              count: { bsonType: "int", minimum: 0 },
              avg_speed: { bsonType: ["double", "int"] },
            },
          },
        },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

// Create indexes
db.traffic_flow_events.createIndex({ intersection_id: 1, timestamp: -1 });
db.traffic_flow_events.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 7776000 }
);

// --- sensor_readings (camera vs speed-based sensors) ---
db.createCollection("sensor_readings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      oneOf: [
        {
          required: [
            "sensor_id",
            "sensor_type",
            "timestamp",
            "detection_results",
            "image_ref",
          ],
          properties: {
            sensor_id: { bsonType: "int", minimum: 1 },
            sensor_type: { bsonType: "string", enum: ["camera"] },
            timestamp: { bsonType: "date" },
            detection_results: { bsonType: "array", minItems: 1 },
            image_ref: { bsonType: "string", minLength: 1 },
          },
          additionalProperties: true,
        },
        {
          required: ["sensor_id", "sensor_type", "timestamp", "velocity_data"],
          properties: {
            sensor_id: { bsonType: "int", minimum: 1 },
            sensor_type: {
              bsonType: "string",
              enum: ["radar", "lidar", "inductive_loop", "acoustic"],
            },
            timestamp: { bsonType: "date" },
            velocity_data: {
              bsonType: "object",
              required: ["min_speed", "max_speed", "avg_speed"],
              properties: {
                min_speed: { bsonType: ["double", "int"] },
                max_speed: { bsonType: ["double", "int"] },
                avg_speed: { bsonType: ["double", "int"] },
              },
            },
          },
          additionalProperties: true,
        },
      ],
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.sensor_readings.createIndex({ sensor_id: 1, timestamp: -1 });
db.sensor_readings.createIndex({ sensor_type: 1, timestamp: -1 });
db.sensor_readings.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 7776000 }
);

// --- incident_reports ---
db.createCollection("incident_reports", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "location",
        "incident_type",
        "incident_description",
        "severity_level",
        "status",
        "reporting_source",
        "reported_timestamp",
        "number_of_lanes_blocked",
      ],
      properties: {
        location: {
          bsonType: "object",
          minProperties: 1,
          properties: {
            intersection_id: { bsonType: ["int", "null"] },
            road_segment_id: { bsonType: ["int", "null"] },
          },
          additionalProperties: false,
        },
        incident_type: {
          bsonType: "string",
          enum: [
            "accident",
            "vehicle_breakdown",
            "road_hazard",
            "construction",
            "special_event",
          ],
        },
        incident_description: { bsonType: "string", minLength: 1 },
        severity_level: {
          bsonType: "string",
          enum: ["minor", "moderate", "major", "critical"],
        },
        status: {
          bsonType: "string",
          enum: ["New", "In-progress", "Resolved", "Closed"],
        },
        reporting_source: {
          bsonType: "string",
          enum: ["sensor", "public", "officer", "camera"],
        },
        reported_timestamp: { bsonType: "date" },
        verified_timestamp: { bsonType: ["date", "null"] },
        resolved_timestamp: { bsonType: ["date", "null"] },
        number_of_lanes_blocked: { bsonType: "int", minimum: 0 },
        witness_statements: { bsonType: "array" },
        vehicles_involved: { bsonType: "array" },
        injuries: { bsonType: "array" },
        property_damages: { bsonType: "array" },
        working_notes: { bsonType: "array" },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.incident_reports.createIndex({
  "location.intersection_id": 1,
  reported_timestamp: -1,
});
db.incident_reports.createIndex({
  "location.road_segment_id": 1,
  reported_timestamp: -1,
});
db.incident_reports.createIndex({
  incident_type: 1,
  severity_level: 1,
  status: 1,
});
db.incident_reports.createIndex(
  { reported_timestamp: 1 },
  { expireAfterSeconds: 7776000 }
);
db.incident_reports.createIndex({ incident_description: "text" });

// --- weather_station_readings ---
db.createCollection("weather_station_readings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "weather_station_id",
        "timestamp",
        "temperature",
        "humidity",
        "precipitation",
        "wind_speed",
        "visibility",
      ],
      properties: {
        weather_station_id: { bsonType: "int", minimum: 1 },
        timestamp: { bsonType: "date" },
        temperature: { bsonType: ["double", "int"] },
        humidity: { bsonType: ["double", "int"] },
        precipitation: { bsonType: "int", minimum: 0, maximum: 100 },
        wind_speed: { bsonType: "int", minimum: 0 },
        visibility: {
          bsonType: "string",
          enum: ["low", "intermediate", "high"],
        },
      },
    },
  },
  validationLevel: "strict",
  validationAction: "error",
});

db.weather_station_readings.createIndex({
  weather_station_id: 1,
  timestamp: -1,
});
db.weather_station_readings.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 7776000 }
);

print("mongo_setup.js: collections, validators, and indexes created.");
