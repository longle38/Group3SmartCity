use traffic_management;

db.traffic_flow_events.deleteMany({});
db.sensor_readings.deleteMany({});
db.incident_reports.deleteMany({});
db.weather_station_readings.deleteMany({});

const CONGESTION = ["low", "moderate", "high", "severe"];

function laneRows(i) {
    const nLanes = 2 + (i % 4);
    const rows = [];
    let total = 0;
    let wsum = 0;
    for (let L = 1; L <= nLanes; L++) {
        const cnt = 15 + ((i * 11 + L * 17) % 120);
        const spd = 12 + ((i + L * 5) % 38) + 0.15 * ((i + L) % 7);
        rows.push({
            lane: NumberInt(L),
            count: NumberInt(cnt),
            avg_speed: spd,
        });
        total += cnt;
        wsum += spd * cnt;
    }
    const avg = total > 0 ? Math.round((wsum / total) * 100) / 100 : 0;
    return { rows: rows, vehicle_count: NumberInt(total), avg_speed: avg };
}

// 500+ traffic_flow_events
const flowDocs = [];
for (let i = 0; i < 520; i++) {
    const lr = laneRows(i);
    const intersection_id = NumberInt((i % 56) + 1);
    const congestion_level = CONGESTION[i % 4];
    const minute = (i * 23 + (i % 91) * 17) % (45 * 24 * 60);
    const ts = new Date(Date.UTC(2026, 3, 5, 10, 0, 0, 0) + minute * 60 * 1000);
    flowDocs.push({
        intersection_id: intersection_id,
        timestamp: ts,
        vehicle_count: lr.vehicle_count,
        avg_speed: lr.avg_speed,
        congestion_level: congestion_level,
        lane_distribution: lr.rows,
    });
}
db.traffic_flow_events.insertMany(flowDocs);

// 200+ sensor readings (camera + radar + lidar)
const CAM = [
    2, 11, 13, 20, 27, 32, 41, 43, 50, 55, 63, 71, 80, 85, 92, 101, 110, 122, 132, 138,
];
const RAD = [
    1, 8, 10, 19, 24, 30, 38, 40, 49, 54, 61, 68, 79, 91, 100, 109, 121, 131, 137, 151,
];
const LID = [
    3, 5, 12, 14, 21, 33, 35, 42, 51, 56, 64, 72, 84, 95, 102, 114, 125, 134, 139, 155,
];

const sensorDocs = [];
for (let i = 0; i < 220; i++) {
    const mod = i % 3;
    const ts = new Date(
        Date.UTC(2026, 3, 8, (i * 3) % 24, (i * 7) % 60, (i * 11) % 60, 0)
    );
    if (mod === 0) {
        sensorDocs.push({
            sensor_id: NumberInt(CAM[i % CAM.length]),
            sensor_type: "camera",
            timestamp: ts,
            detection_results: [
                {
                    type: "car",
                    count: NumberInt(5 + (i % 25)),
                    confidence: Math.round((0.82 + (i % 15) / 100) * 100) / 100,
                },
                {
                    type: "truck",
                    count: NumberInt(i % 6),
                    confidence: Math.round((0.76 + (i % 12) / 100) * 100) / 100,
                },
            ],
            image_ref: "s3://traffic-images/2026/04/camera-reading-" + i + ".jpg",
        });
    } else if (mod === 1) {
        sensorDocs.push({
            sensor_id: NumberInt(RAD[i % RAD.length]),
            sensor_type: "radar",
            timestamp: ts,
            velocity_data: {
                min_speed: 8 + (i % 18),
                max_speed: 38 + (i % 25),
                avg_speed: 22 + (i % 20),
            },
        });
    } else {
        sensorDocs.push({
            sensor_id: NumberInt(LID[i % LID.length]),
            sensor_type: "lidar",
            timestamp: ts,
            velocity_data: {
                min_speed: 10 + (i % 15),
                max_speed: 42 + (i % 22),
                avg_speed: 24 + (i % 18),
            },
        });
    }
}
db.sensor_readings.insertMany(sensorDocs);

// 85 incident_reports
const INC_TYPES = [
    "accident",
    "vehicle_breakdown",
    "road_hazard",
    "construction",
    "special_event",
];
const SEVERITY = ["minor", "moderate", "major", "critical"];
const STATUSES = ["New", "In-progress", "Resolved", "Closed"];
const SOURCES = ["sensor", "public", "officer", "camera"];

const incidentDocs = [];
for (let i = 0; i < 85; i++) {
    const useRoad = i % 6 === 0;
    const loc = useRoad
        ? { road_segment_id: NumberInt((i % 55) + 1) }
        : { intersection_id: NumberInt((i % 56) + 1) };
    const reported = new Date(
        Date.UTC(2026, 3, 1, 14, 0, 0, 0) + i * 3600000 * 9 + (i % 17) * 600000
    );
    const resolved =
        i % 5 === 0
            ? null
            : new Date(reported.getTime() + ((i % 48) + 1) * 3600000);
    const verified =
        i % 7 === 0 ? null : new Date(reported.getTime() + ((i % 8) + 1) * 600000);

    incidentDocs.push({
        location: loc,
        incident_type: INC_TYPES[i % INC_TYPES.length],
        incident_description:
            "Incident " +
            i +
            ": " +
            (useRoad ? "road segment" : "intersection") +
            " report — automated seed narrative for GP3 queries.",
        severity_level: SEVERITY[i % SEVERITY.length],
        status: STATUSES[i % STATUSES.length],
        reporting_source: SOURCES[i % SOURCES.length],
        reported_timestamp: reported,
        verified_timestamp: verified,
        resolved_timestamp: resolved,
        number_of_lanes_blocked: NumberInt(i % 4),
        witness_statements:
            i % 3 === 0
                ? []
                : [{ name: "Witness " + i, statement: "Observed conditions at scene." }],
        vehicles_involved:
            i % 4 === 0
                ? []
                : [{ plate: "ABC-" + (1000 + i), role: "involved" }],
        injuries:
            i % 5 === 0 ? [] : [{ severity: "minor", count: NumberInt(1) }],
        property_damages:
            i % 6 === 0 ? [] : [{ item: "guardrail", estimate_usd: 1200 + i }],
        working_notes:
            i % 2 === 0
                ? []
                : [{ author: "dispatch", note: "Follow-up scheduled", at: reported }],
    });
}
db.incident_reports.insertMany(incidentDocs);

// 120 weather_station_readings (6 stations from PostgreSQL)
const weatherDocs = [];
const VIS = ["low", "intermediate", "high"];
for (let i = 0; i < 120; i++) {
    const wid = NumberInt((i % 6) + 1);
    const ts = new Date(
        Date.UTC(2026, 3, 12, (i * 2) % 24, (i * 5) % 60, 0, 0)
    );
    weatherDocs.push({
        weather_station_id: wid,
        timestamp: ts,
        temperature: Math.round((48 + (i % 18) + (i % 7) * 0.35) * 10) / 10,
        humidity: Math.round((42 + (i % 40) + (i % 5)) * 10) / 10,
        precipitation: NumberInt((i * 7) % 101),
        wind_speed: NumberInt(4 + (i % 15)),
        visibility: VIS[i % 3],
    });
}
db.weather_station_readings.insertMany(weatherDocs);

printjson({
    traffic_flow_events: db.traffic_flow_events.countDocuments(),
    sensor_readings: db.sensor_readings.countDocuments(),
    incident_reports: db.incident_reports.countDocuments(),
    weather_station_readings: db.weather_station_readings.countDocuments(),
});
