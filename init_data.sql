use iot;

INSERT INTO iot.t_metric_type (type_name, type_description, type_unit) VALUES ('温度', '温度', 'C');
INSERT INTO iot.t_metric_type (type_name, type_description, type_unit) VALUES ('漏电流', '漏电流', 'A');
INSERT INTO iot.t_metric_type (type_name, type_description, type_unit) VALUES ('电压', '电压', 'V');

INSERT INTO iot.t_device_model (name, description) VALUES ('model911', '型号1');

INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (1, 'CA', 'CSA', '电流A', '漏电流', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (2, 'CB', 'CSB', '电流B', '漏电流', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (3, 'CC', 'CSC', '电流C', '漏电流', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (4, 'T1', 'TS1', '温度1', '温度', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (5, 'VA', 'VSA', '电压A', '漏电流', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (6, 'VB', 'VSB', '电压B', '漏电流', 'model911');
INSERT INTO iot.t_metric_config (metric_id, metric_key, metric_status_key, metric_display_name, metric_type, device_model) VALUES (7, 'VC', 'VSC', '电压C', '漏电流', 'model911');

INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (1, '工程商A', '工程商', null);
INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (2, '项目A-1','项目', 1);
INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (3, '项目A-2', '项目', 1);
INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (4, '工程商B', '工程商', null);
INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (5, '项目B-1', '项目', 4);
INSERT INTO iot.t_customer (id, name, type, parent_id) VALUES (6, '项目B-2', '项目', 4);


INSERT INTO iot.t_role (name, description) VALUES ('admin', '管理员');

INSERT INTO iot.t_device (device_id, device_name, device_model, device_sim, project, secret, mongo_slice, longitude, latitude, location, registry_time, network_status, device_status, status_time) VALUES (1, '测试设备1', 'model911', '123456', 2, '12345', 0, '10''123''123', '10''123''123', '珠海丽景大宾馆', '2019-01-25 22:00:41', 'online', 0, '2019-01-25 22:00:41');

INSERT INTO iot.t_user (id, name, description, password, phone, email) VALUES (1, '测试用户', null, ' b7765f76a53496c73c6633f3432f5fbf', null, 'abc@126.com');

INSERT INTO iot.t_user_permission (user_id, customer_id, role_name) VALUES (1, 1, 'admin');