-- Query #1: [Most Incident-Prone Intersections and Installed Sensors]
-- Business Question: Which intersections have the most incidents, and what sensors are installed there?
-- Complexity Features: [window_function, COALESCE, DISTINCT,  JOINs, aggregates, subqueries]
-- Tables Used: [intersection, incident, sensor]

WITH incident_counts AS (
    SELECT
        i.intersection_id,
        COUNT(*) AS incident_count
    FROM incident i
    WHERE i.intersection_id IS NOT NULL
    GROUP BY i.intersection_id
),
ranked_intersections AS (
    SELECT
        ic.intersection_id,
        ic.incident_count,
        DENSE_RANK() OVER (ORDER BY ic.incident_count DESC) AS incident_rank
    FROM incident_counts ic
)
SELECT
    ri.intersection_id,
    i.intersection_name,
    ri.incident_count,
    COALESCE(
        STRING_AGG(
            DISTINCT (s.sensor_type || ' [' || s.sensor_status || ']'),
            ', '
            ORDER BY (s.sensor_type || ' [' || s.sensor_status || ']')
        ),
        'No sensors installed'
    ) AS installed_sensors
FROM ranked_intersections ri
JOIN intersection i
    ON i.intersection_id = ri.intersection_id
LEFT JOIN sensor s
    ON s.intersection_id = ri.intersection_id
WHERE ri.incident_rank = 1
GROUP BY ri.intersection_id, i.intersection_name, ri.incident_count
ORDER BY ri.intersection_id;

-- Expected Output:
---- intersection_id: Unique identifier for the intersection.
---- intersection_name: Name of the intersection.
---- incident_count: Total number of incidents recorded at the intersection.
---- installed_sensors: A comma-separated list of sensors and their current statuses.
-- Sample Results:
----  intersection_id | intersection_name     | incident_count | installed_sensors
---- -----------------+-----------------------+----------------+----------------------------------------------------------------
----  6               | K St NW & 18th St NW  | 2              | No sensors installed
----  10              | I St NW & 22nd St NW  | 2              | acoustic [active], camera [maintenance], lidar [offline], radar [maintenance]
----  16              | I St NW & 16th St NW  | 2              | acoustic [active], inductive_loop [active], lidar [active], radar [active]

-- Query #2: [Maintenance Tasks with Crew and Intersection Information]
-- Business Question: List all maintenance tasks with crew details and intersection information.
-- Complexity Features: [UNION, JOINs, aggregates, subqueries]
-- Tables Used: [maintenance_task, maintenance_crew, sensor_maintenance_task, traffic_signal_maintenance_task, road_segment_maintenance_task, weather_station_maintenance_task, sensor, traffic_signal, road_segment, weather_station, intersection]

WITH task_locations AS (
    SELECT
        smt.task_id,
        'sensor' AS asset_type,
        smt.sensor_id::TEXT AS asset_id,
        i.intersection_id,
        i.intersection_name
    FROM sensor_maintenance_task smt
    JOIN sensor s
        ON smt.sensor_id = s.sensor_id
    JOIN intersection i
        ON s.intersection_id = i.intersection_id

    UNION ALL

    SELECT
        tsmt.task_id,
        'traffic_signal' AS asset_type,
        tsmt.signal_id::TEXT AS asset_id,
        i.intersection_id,
        i.intersection_name
    FROM traffic_signal_maintenance_task tsmt
    JOIN traffic_signal ts
        ON tsmt.signal_id = ts.signal_id
    JOIN intersection i
        ON ts.intersection_id = i.intersection_id

    UNION ALL

    SELECT
        rsmt.task_id,
        'road_segment' AS asset_type,
        rsmt.segment_id::TEXT AS asset_id,
        i.intersection_id,
        i.intersection_name
    FROM road_segment_maintenance_task rsmt
    JOIN road_segment rs
        ON rsmt.segment_id = rs.segment_id
    JOIN intersection i
        ON i.intersection_id IN (rs.from_intersection_id, rs.to_intersection_id)

    UNION ALL

    SELECT
        wsmt.task_id,
        'weather_station' AS asset_type,
        wsmt.weather_station_id::TEXT AS asset_id,
        i.intersection_id,
        i.intersection_name
    FROM weather_station_maintenance_task wsmt
    JOIN weather_station ws
        ON wsmt.weather_station_id = ws.weather_station_id
    JOIN intersection i
        ON ws.intersection_id = i.intersection_id
)
SELECT
    mt.task_id,
    mt.maintenance_status,
    mt.maintenance_type,
    mt.scheduled_date,
    mt.scheduled_time,
    mt.priority_level,
    mt.estimated_duration_minutes,
    mt.actual_duration_minutes,
    mc.crew_id,
    mc.supervisor,
    mc.specialization,
    mc.certification_level,
    mc.available,
    STRING_AGG(
        DISTINCT (tl.asset_type || ':' || tl.asset_id),
        ', '
        ORDER BY (tl.asset_type || ':' || tl.asset_id)
    ) AS assets,
    STRING_AGG(
        DISTINCT (tl.intersection_id || ' - ' || tl.intersection_name),
        ', '
        ORDER BY (tl.intersection_id || ' - ' || tl.intersection_name)
    ) AS intersections
FROM maintenance_task mt
LEFT JOIN maintenance_crew mc
    ON mt.assigned_crew = mc.crew_id
LEFT JOIN task_locations tl
    ON mt.task_id = tl.task_id
GROUP BY
    mt.task_id,
    mt.maintenance_status,
    mt.maintenance_type,
    mt.scheduled_date,
    mt.scheduled_time,
    mt.priority_level,
    mt.estimated_duration_minutes,
    mt.actual_duration_minutes,
    mc.crew_id,
    mc.supervisor,
    mc.specialization,
    mc.certification_level,
    mc.available
ORDER BY mt.task_id;


-- Expected Output:
---- task_id: Unique identifier for the maintenance task.
---- maintenance_status: Current status of the maintenance task (e.g., 'scheduled', 'in_progress', 'completed').
---- maintenance_type: Type of maintenance (e.g., 'preventive', 'corrective').
---- scheduled_date: Date when the maintenance is scheduled.
---- scheduled_time: Time when the maintenance is scheduled.
---- priority_level: Priority level of the maintenance task (e.g., 'low', 'medium', 'high', 'critical').
---- estimated_duration_minutes: Estimated duration of the maintenance task in minutes.
---- actual_duration_minutes: Actual duration of the maintenance task in minutes (if completed).
---- crew_id: Unique identifier for the maintenance crew assigned to the task.
---- supervisor: Name of the crew supervisor.
---- specialization: Area of specialization for the crew (e.g., 'electrical', 'mechanical').
---- certification_level: Certification level of the crew (e.g., 'basic', 'advanced').
---- available: Availability status of the crew (true/false).
---- assets: A comma-separated list of assets involved in the maintenance task, formatted as 'asset_type:asset_id'.
---- intersections: A comma-separated list of intersections associated with the maintenance task, formatted as 'intersection_id - intersection_name'.
-- Sample Results: 
---- task_id | maintenance_status | maintenance_type | scheduled_date | scheduled_time       | priority_level | estimated_duration_minutes | actual_duration_minutes | crew_id | supervisor    | specialization | certification_level | available | assets             | intersections
---- --------+--------------------+------------------+----------------+----------------+---------+---------------+----------------+---------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------
---- 1       | completed          | corrective       | 2026-01-21     | 2026-01-21 09:13:00  | moderate       | 45                         | 40                      | 2       | Marcus Reed   | mechanical     | Level II            | TRUE      | sensor:5           | 2 - K St NW & 22nd St NW
---- 41      | completed          | corrective       | 2026-03-01     | 2026-03-01 09:53:00  | moderate       | 120                        | 115                     | 9       | Lauren Price  | electrical     | Level I             | TRUE      | traffic_signal:124 | 37 - F St NW & 19th St NW
---- 71      | completed          | upgrade          | 2026-02-28     | 2026-02-28 09:23:00  | moderate       | 45                         | 40                      | 6       | Jamal Carter  | civil          | Level II            | TRUE      | road_segment:33    | 37 - F St NW & 19th St NW, 38 - F St NW & 18th St NW


-- Query #3: [Critical Incidents at Intersections]
-- Business Question: Find signals at intersections that have had critical incidents in the last 30 days.
-- Complexity Features: [JOINs, aggregates, subqueries]
-- Tables Used: [traffic_signal, intersection, incident]


SELECT DISTINCT
    ts.signal_id,
    ts.intersection_id,
    i.intersection_name,
    ts.approach_direction,
    ts.signal_type,
    ts.timing_mode,
    ts.power_source,
    inc.incident_number,
    inc.incident_type,
    inc.severity_level,
    inc.reporting_source,
    inc.number_of_lanes_blocked,
    inc.reported_timestamp,
    inc.verified_timestamp,
    inc.resolved_timestamp
FROM traffic_signal ts
JOIN intersection i
    ON ts.intersection_id = i.intersection_id
JOIN incident inc
    ON inc.intersection_id = ts.intersection_id
WHERE inc.severity_level = 'critical'
  AND inc.reported_timestamp >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY RANDOM();

-- Expected Output: [Description of result columns]
---- signal_id: Unique identifier for the traffic signal.
---- intersection_id: Unique identifier for the intersection where the signal is located.
---- intersection_name: Name of the intersection.
---- approach_direction: Direction of the approach where the signal is located (e.g., 'north', 'south', 'east', 'west').
---- signal_type: Type of traffic signal (e.g., 'LED', 'incandescent', 'pedestrian').
---- timing_mode: Timing mode of the traffic signal (e.g., 'fixed', 'adaptive', 'emergency').
---- power_source: Power source for the traffic signal (e.g., 'grid', 'solar').
---- incident_number: Unique identifier for the incident.
---- incident_type: Type of incident (e.g., 'accident', 'vehicle_breakdown', 'special_event').
---- severity_level: Severity level of the incident (e.g., 'minor', 'moderate', 'critical').
---- reporting_source: Source that reported the incident (e.g., 'sensor', 'officer', 'public').
---- number_of_lanes_blocked: Number of lanes blocked due to the incident.
---- reported_timestamp: Timestamp when the incident was reported.
---- verified_timestamp: Timestamp when the incident was verified.
---- resolved_timestamp: Timestamp when the incident was resolved.
-- Sample Results: 
---- signal_id | intersection_id | intersection_name    | approach_direction | signal_type  | timing_mode | power_source | incident_number | incident_type      | severity_level | reporting_source | number_of_lanes_blocked | reported_timestamp  | verified_timestamp  | resolved_timestamp
---- ----------+-----------------+----------------------+--------------------+--------------+-------------+--------------+-----------------+--------------------+----------------+------------------+-------------------------+---------------------+---------------------+---------------------
---- 134       | 40              | F St NW & 16th St NW | south              | pedestrian   | adaptive    | grid         | 75              | accident           | critical       | sensor           | 4                       | 2026-04-03 17:45:00 | 2026-04-03 17:53:00 | 2026-04-03 19:35:00
---- 101       | 30              | G St NW & 18th St NW | east               | LED          | fixed       | grid         | 73              | vehicle_breakdown  | critical       | officer          | 4                       | 2026-03-20 19:23:00 | 2026-03-20 19:29:00 | 2026-03-20 21:11:00
---- 167       | 50              | D St NW & 22nd St NW | north              | incandescent | emergency   | grid         | 77              | special_event      | critical       | officer          | 4                       | 2026-04-17 08:07:00 | 2026-04-17 08:17:00 | 2026-04-17 09:59:00

-- Query #4: [Incident Resolution Time by Severity Level]
-- Business Question: Calculate average incident resolution time by severity level.
-- Complexity Features: [aggregates, subqueries, AVG]
-- Tables Used: [incident]

SELECT
    severity_level,
    AVG(resolved_timestamp - reported_timestamp) AS avg_resolution_time
FROM incident
WHERE resolved_timestamp IS NOT NULL
GROUP BY severity_level
ORDER BY severity_level;

-- Expected Output:
---- severity_level: Severity level of the incident (e.g., 'minor', 'moderate', 'critical').
---- avg_resolution_time: Average time taken to resolve incidents of that severity level, calculated as the
-- Sample Results: 
---- severity_level | avg_resolution_time
---- ---------------+---------------------
---- critical       | 01:49:20
---- major          | 01:37:25
---- moderate       | 01:17:20


-- Query #5: [Intersections with Fewer Sensors]
-- Business Question: Count sensors per intersection and find intersections with fewer than 2 sensors.
-- Complexity Features: [JOINs, aggregates, subqueries]
-- Tables Used: [intersection, sensor]

SELECT
    i.intersection_id,
    i.intersection_name,
    COUNT(s.sensor_id) AS sensor_count
FROM intersection i
LEFT JOIN sensor s
    ON i.intersection_id = s.intersection_id
GROUP BY i.intersection_id, i.intersection_name
HAVING COUNT(s.sensor_id) < 2
ORDER BY sensor_count, i.intersection_id;

-- Expected Output:
---- intersection_id: Unique identifier for the intersection.
---- intersection_name: Name of the intersection.
---- sensor_count: Total number of sensors installed at the intersection.
-- Sample Results:
---- intersection_id | intersection_name    | sensor_count
---- ----------------+----------------------+-------------
---- 6               | K St NW & 18th St NW | 0
---- 15              | I St NW & 17th St NW | 0
---- 24              | H St NW & 16th St NW | 0


-- Query #6: [Intersections with More Incidents than Average]
-- Business Question: Find intersections with more incidents than the citywide average.
-- Complexity Features: [JOINs, aggregates, subqueries]
-- Tables Used: [incident, intersection]

WITH incident_counts AS (
    SELECT
        intersection_id,
        COUNT(*) AS incident_count
    FROM incident
    WHERE intersection_id IS NOT NULL
    GROUP BY intersection_id
),
citywide_average AS (
    SELECT ROUND(AVG(incident_count), 2) AS avg_incident_count
    FROM incident_counts
)
SELECT
    i.intersection_id,
    i.intersection_name,
    ic.incident_count,
    ca.avg_incident_count
FROM incident_counts ic
JOIN intersection i
    ON ic.intersection_id = i.intersection_id
CROSS JOIN citywide_average ca
WHERE ic.incident_count > ca.avg_incident_count
ORDER BY ic.incident_count DESC, i.intersection_id;

-- Expected Output:
---- intersection_id: Unique identifier for the intersection.
---- intersection_name: Name of the intersection.
---- incident_count: Total number of incidents recorded at the intersection.
---- avg_incident_count: Average number of incidents per intersection citywide, rounded to 2
-- Sample Results: 
---- intersection_id | intersection_name      | incident_count | avg_incident_count
---- ----------------+------------------------+----------------+-------------------
---- 6               | K St NW & 18th St NW   | 2              | 1.39
---- 10              | I St NW & 22nd St NW   | 2              | 1.39
---- 16              | I St NW & 16th St NW   | 2              | 1.39


-- Query #7: [Crews with No Critical Maintenance Tasks]
-- Business Question: List crews that have never been assigned to a critical-priority maintenance task.
-- Complexity Features: [JOINs, aggregates, subqueries]
-- Tables Used: [maintenance_crew, maintenance_task]

SELECT
    mc.crew_id,
    mc.supervisor,
    mc.specialization,
    mc.certification_level,
    mc.available
FROM maintenance_crew mc
WHERE NOT EXISTS (
    SELECT 1
    FROM maintenance_task mt
    WHERE mt.assigned_crew = mc.crew_id
      AND mt.priority_level = 'critical'
)
ORDER BY mc.crew_id;

-- Expected Output: [Description of result columns]
---- crew_id: Unique identifier for the maintenance crew.
---- supervisor: Name of the crew's supervisor.
---- specialization: Area of expertise for the maintenance crew.
---- certification_level: Level of certification for the maintenance crew.
---- available: Availability status of the maintenance crew.
-- Sample Results: 
---- crew_id | supervisor | specialization | certification_level | available
---- --------+------------+----------------+---------------------+----------
---- (0 rows)


