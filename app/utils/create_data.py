from app import db
from app.models.customer import Customer
from app.models.device import Device
from app.models.device_model import DeviceModel
from app.models.metric_config import MetricConfig
from app.models.metric_type import MetricType
from app.models.project import Project
import datetime


def db_data(app):

    with app.app_context():

        db.create_all()

        c = Customer(name="pilot", description="珠海派诺")
        p = Project(name="test", description="测试项目", customer=c)
        md = DeviceModel(name='model911', description='型号1')
        db.session.add(c)
        db.session.add(p)
        db.session.add(md)
        db.session.add(Device(
            device_id=1,
            device_name='测试设备1',
            device_sim='123456',
            device_model=md,
            secret="12345",
            registry_time=datetime.datetime.now(),
            location="珠海丽景大宾馆",
            longitude="10'123'123",
            latitude="10'123'123",
            project=p,
            mongo_slice=0,
            network_status='online',
            device_status=0,
            status_time=datetime.datetime.now()
        ))

        mt = MetricType(
            type_name='漏电流',
            type_description='漏电流',
            type_unit='A'
        )
        db.session.add(mt)

        mt2 = MetricType(
            type_name='温度',
            type_description='温度',
            type_unit='C'
        )
        db.session.add(mt2)

        ca = MetricConfig(
            metric_key='CA',
            metric_status_key='CSA',
            metric_display_name='电流A',
            device_model=md,
            metric_type=mt
        )

        cb = MetricConfig(
            metric_key='CB',
            metric_status_key='CSB',
            metric_display_name='电流B',
            device_model=md,
            metric_type=mt
        )
        cc = MetricConfig(
            metric_key='CC',
            metric_status_key='CSC',
            metric_display_name='电流C',
            device_model=md,
            metric_type=mt
        )

        va = MetricConfig(
            metric_key='VA',
            metric_status_key='VSA',
            metric_display_name='电压A',
            device_model=md,
            metric_type=mt
        )

        vb = MetricConfig(
            metric_key='VB',
            metric_status_key='VSB',
            metric_display_name='电压B',
            device_model=md,
            metric_type=mt
        )
        vc = MetricConfig(
            metric_key='VC',
            metric_status_key='VSC',
            metric_display_name='电压C',
            device_model=md,
            metric_type=mt
        )

        t1 = MetricConfig(
            metric_key='T1',
            metric_status_key='TS1',
            metric_display_name='温度1',
            device_model=md,
            metric_type=mt2
        )

        md.metrics.append(ca)
        md.metrics.append(cb)
        md.metrics.append(cc)
        md.metrics.append(t1)
        md.metrics.append(va)
        md.metrics.append(vb)
        md.metrics.append(vc)
        db.session.commit()
