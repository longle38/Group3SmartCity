CREATE TYPE incident_type_enum AS ENUM (
    'accident',
    'vehicle_breakdown',
    'road_hazard',
    'construction',
    'special_event'
);

CREATE TYPE maintenance_status_enum AS ENUM (
    'scheduled',
    'in_progress',
    'completed'
);

CREATE TYPE priority_level_enum AS ENUM (
    'low',
    'moderate',
    'high',
    'critical',
    'severe'
);

CREATE TYPE severity_level_enum AS ENUM (
    'minor',
    'moderate',
    'major',
    'critical'
);

CREATE TYPE reporting_source_enum AS ENUM (
    'sensor',
    'public',
    'officer',
    'camera'
);

CREATE TYPE sensor_type_enum AS ENUM (
    'inductive_loop',
    'radar',
    'camera',
    'lidar',
    'acoustic'
);

CREATE TYPE signal_type_enum AS ENUM (
    'LED',
    'incandescent',
    'pedestrian'
);

CREATE TYPE timing_mode_enum AS ENUM (
    'adaptive',
    'fixed',
    'emergency'
);

CREATE TYPE approach_direction_enum AS ENUM (
    'north',
    'south',
    'east',
    'west'
);

CREATE TYPE maintenance_type_enum AS ENUM (
    'preventive',
    'corrective',
    'inspection',
    'upgrade'
);

CREATE TYPE specialization_enum AS ENUM (
    'electrical',
    'mechanical',
    'civil',
    'software'
);

CREATE TYPE surface_type_enum AS ENUM (
    'asphalt',
    'concrete'
);

CREATE TYPE zone_type_enum AS ENUM (
    'downtown',
    'residential',
    'industrial',
    'school',
    'commercial'
);

CREATE TYPE special_restriction_type_enum AS ENUM (
    'time-based',
    'vehicle-type'
);

CREATE TYPE facility_type_enum AS ENUM (
    'surface_lot',
    'parking_garage',
    'street_parking',
    'hospital',
    'fire_station',
    'police_station'
);

CREATE TYPE day_of_week_enum AS ENUM (
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun'
);

CREATE TYPE pricing_structure_enum AS ENUM (
    'flat_rate',
    'hourly'
);

CREATE TABLE intersection (
    intersection_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    intersection_name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    intersection_type VARCHAR(30) NOT NULL,
    traffic_handling_capacity INTEGER NOT NULL,
    installation_date DATE NOT NULL,
    jurisdiction_district VARCHAR(100) NOT NULL,
    elevation DECIMAL(10, 2) NOT NULL,
    CHECK (latitude >= -90 AND latitude <= 90),
    CHECK (longitude >= -180 AND longitude <= 180),
    CHECK (traffic_handling_capacity > 0)
);

CREATE TABLE signalized_intersection (
    intersection_id INTEGER PRIMARY KEY
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE
);

CREATE TABLE sensor (
    sensor_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    intersection_id INTEGER NOT NULL
        REFERENCES signalized_intersection(intersection_id)
        ON DELETE CASCADE,
    sensor_status VARCHAR(30) NOT NULL,
    sensor_type sensor_type_enum NOT NULL,
    installation_date DATE NOT NULL,
    UNIQUE (intersection_id, sensor_type)
);

CREATE TABLE sensor_reading (
    sensor_reading_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sensor_id INTEGER NOT NULL
        REFERENCES sensor(sensor_id)
        ON DELETE CASCADE,
    vehicle_speed INTEGER,
    occupancy INTEGER,
    traffic_flow INTEGER,
    reading_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (vehicle_speed IS NULL OR vehicle_speed >= 0),
    CHECK (occupancy IS NULL OR occupancy >= 0),
    CHECK (traffic_flow IS NULL OR traffic_flow >= 0)
);

CREATE TABLE traffic_signal (
    signal_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    intersection_id INTEGER NOT NULL
        REFERENCES signalized_intersection(intersection_id)
        ON DELETE CASCADE,
    approach_direction approach_direction_enum NOT NULL,
    power_source VARCHAR(30) NOT NULL,
    signal_type signal_type_enum NOT NULL,
    timing_mode timing_mode_enum NOT NULL,
    warranty_information TEXT
);

CREATE TABLE maintenance_crew (
    crew_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    supervisor VARCHAR(50) NOT NULL,
    specialization specialization_enum NOT NULL,
    certification_level VARCHAR(50) NOT NULL,
    available BOOLEAN NOT NULL
);

CREATE TABLE road_segment (
    segment_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    street_name VARCHAR(100) NOT NULL,
    has_sidewalk BOOLEAN NOT NULL,
    has_bike_lane BOOLEAN NOT NULL,
    grade DECIMAL(5, 2) NOT NULL,
    length DECIMAL(10, 2) NOT NULL,
    surface_type surface_type_enum NOT NULL,
    speed_limit INTEGER NOT NULL,
    lane_width DECIMAL(10, 2) NOT NULL,
    number_of_lanes INTEGER NOT NULL,
    from_intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    to_intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    UNIQUE (from_intersection_id, to_intersection_id, street_name),
    -- Enforce a consistent direction for segments to prevent duplicates in opposite directions
    -- It also ensures that a segment cannot start and end at the same intersection
    CHECK (from_intersection_id < to_intersection_id),
    CHECK (grade >= -45 AND grade <= 45),
    CHECK (length > 0 and speed_limit > 0 and lane_width > 0 and number_of_lanes > 0)
);

CREATE TABLE weather_station (
    weather_station_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    operational_status VARCHAR(30) NOT NULL,
    data_transmission_frequency_seconds INTEGER NOT NULL,
    CHECK (data_transmission_frequency_seconds > 0)
);

CREATE TABLE weather_station_capability (
    capability VARCHAR(50) NOT NULL,
    weather_station_id INTEGER NOT NULL,
    CONSTRAINT pk_weather_station_capability
        PRIMARY KEY (weather_station_id, capability),
    CONSTRAINT fk_weather_station_capability
        FOREIGN KEY (weather_station_id)
            REFERENCES weather_station(weather_station_id)
            ON DELETE CASCADE
);

CREATE TABLE weather_reading (
    reading_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    weather_station_id INTEGER NOT NULL
        REFERENCES weather_station(weather_station_id)
        ON DELETE CASCADE,
    reading_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    precipitation DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    visibility DECIMAL(10, 2),
    CHECK (humidity IS NULL OR humidity BETWEEN 0 AND 100),
    CHECK (precipitation IS NULL OR precipitation >= 0),
    CHECK (wind_speed IS NULL OR wind_speed >= 0),
    CHECK (visibility IS NULL OR visibility >= 0)
);

CREATE TABLE incident (
    incident_number INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    incident_type incident_type_enum NOT NULL,
    severity_level severity_level_enum NOT NULL,
    reporting_source reporting_source_enum NOT NULL,
    reported_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_timestamp TIMESTAMP,
    resolved_timestamp TIMESTAMP,
    number_of_lanes_blocked INTEGER NOT NULL,
    intersection_id INTEGER
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    road_segment_id INTEGER
        REFERENCES road_segment(segment_id)
        ON DELETE CASCADE,
    CHECK (intersection_id IS NOT NULL OR road_segment_id IS NOT NULL),
    CHECK (number_of_lanes_blocked >= 0),
    CHECK (verified_timestamp IS NULL OR verified_timestamp >= reported_timestamp),
    CHECK (resolved_timestamp IS NULL OR resolved_timestamp >= reported_timestamp)
);

CREATE TABLE maintenance_task (
    task_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    maintenance_status maintenance_status_enum NOT NULL,
    maintenance_type maintenance_type_enum NOT NULL,
    scheduled_date DATE DEFAULT CURRENT_DATE,
    scheduled_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_duration_minutes INTEGER NOT NULL,
    priority_level priority_level_enum NOT NULL,
    assigned_crew INTEGER
        REFERENCES maintenance_crew(crew_id),
    actual_duration_minutes INTEGER,
    CHECK (estimated_duration_minutes > 0),
    CHECK (actual_duration_minutes IS NULL OR actual_duration_minutes >= 0)
);

CREATE TABLE sensor_maintenance_task (
    task_id INTEGER NOT NULL
        REFERENCES maintenance_task(task_id)
        ON DELETE CASCADE,
    sensor_id INTEGER NOT NULL
        REFERENCES sensor(sensor_id)
        ON DELETE CASCADE,
    PRIMARY KEY (task_id, sensor_id)
);

CREATE TABLE traffic_signal_maintenance_task (
    task_id INTEGER NOT NULL
        REFERENCES maintenance_task(task_id)
        ON DELETE CASCADE,
    signal_id INTEGER NOT NULL
        REFERENCES traffic_signal(signal_id)
        ON DELETE CASCADE,
    PRIMARY KEY (task_id, signal_id)
);

CREATE TABLE road_segment_maintenance_task (
    task_id INTEGER NOT NULL
        REFERENCES maintenance_task(task_id)
        ON DELETE CASCADE,
    segment_id INTEGER NOT NULL
        REFERENCES road_segment(segment_id)
        ON DELETE CASCADE,
    PRIMARY KEY (task_id, segment_id)
);

CREATE TABLE weather_station_maintenance_task (
    task_id INTEGER NOT NULL
        REFERENCES maintenance_task(task_id)
        ON DELETE CASCADE,
    weather_station_id INTEGER NOT NULL
        REFERENCES weather_station(weather_station_id)
        ON DELETE CASCADE,
    PRIMARY KEY (task_id, weather_station_id)
);

CREATE TABLE traffic_control_zone (
    zone_number INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    default_speed_limit INTEGER NOT NULL,
    enforcement_level INTEGER NOT NULL,
    zone_type zone_type_enum NOT NULL,
    restriction_type special_restriction_type_enum,
    restriction_details TEXT,
    CHECK (default_speed_limit > 0 and default_speed_limit <= 90),
    CHECK (enforcement_level >= 1 AND enforcement_level <= 5)
);

CREATE TABLE zone_control_management (
    zone_number INTEGER NOT NULL
        REFERENCES traffic_control_zone(zone_number)
        ON DELETE CASCADE,
    intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    PRIMARY KEY (zone_number, intersection_id)
);

CREATE TABLE facility (
    facility_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL,
    total_capacity INTEGER NOT NULL,
    facility_type facility_type_enum NOT NULL,
    CHECK (total_capacity > 0)
);

CREATE TABLE operation_hour (
    operation_hour_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    facility_id INTEGER NOT NULL
        REFERENCES facility(facility_id)
        ON DELETE CASCADE,
    day_of_week day_of_week_enum NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    CHECK (open_time < close_time),
    UNIQUE (facility_id, day_of_week)
);

CREATE TABLE parking_facility (
    facility_id INTEGER PRIMARY KEY
        REFERENCES facility(facility_id)
        ON DELETE CASCADE,
    ev_charging_stations INTEGER NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    pricing_structure pricing_structure_enum NOT NULL,
    accessible_spaces INTEGER NOT NULL,
    CHECK (accessible_spaces >= 0),
    CHECK (ev_charging_stations >= 0)
);

CREATE TABLE emergency_facility (
    facility_id INTEGER PRIMARY KEY
        REFERENCES facility(facility_id)
        ON DELETE CASCADE,
    capability VARCHAR(50) NOT NULL,
    phone_number VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE emergency_route (
    route_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    start_intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    end_intersection_id INTEGER NOT NULL
        REFERENCES intersection(intersection_id)
        ON DELETE CASCADE,
    emergency_facility_id INTEGER NOT NULL
        REFERENCES emergency_facility(facility_id)
        ON DELETE CASCADE,
    priority_level INTEGER NOT NULL,
    estimated_travel_time INTEGER NOT NULL,
    route_length DECIMAL(10, 2) NOT NULL,
    recommended_speed INTEGER NOT NULL,
    alternative_route_id INTEGER
        REFERENCES emergency_route(route_id),
    CHECK (start_intersection_id <> end_intersection_id),
    CHECK (alternative_route_id IS NULL OR alternative_route_id <> route_id),
    CHECK (priority_level >= 1 AND priority_level <= 5),
    CHECK (estimated_travel_time > 0),
    CHECK (route_length > 0),
    CHECK (recommended_speed > 0 and recommended_speed <= 90)
);

CREATE TABLE emergency_route_path (
    route_id INTEGER NOT NULL
        REFERENCES emergency_route(route_id)
        ON DELETE CASCADE,
    segment_id INTEGER NOT NULL
        REFERENCES road_segment(segment_id)
        ON DELETE CASCADE,
    path_order INTEGER NOT NULL,
    CONSTRAINT pk_emergency_route_path
        PRIMARY KEY (route_id, path_order),
    CHECK (path_order >= 0),
    UNIQUE (route_id, segment_id)
);

CREATE TABLE emergency_route_usage (
    emergency_route_usage_id INTEGER
        GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    route_id INTEGER NOT NULL
        REFERENCES emergency_route(route_id)
        ON DELETE CASCADE,
    usage_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    response_time_in_minutes INTEGER NOT NULL,
    CHECK (response_time_in_minutes > 0)
);
