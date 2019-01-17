create table inverter_reading (
  inverter text not null,
  timestamp timestamptz not null,
  kwh_total numeric not null,
  kwh_today numeric not null,
  inverter_temperature numeric not null,
  inverter_hours integer not null,

  pv1_voltage numeric not null,
  pv2_voltage numeric not null,
  pv3_voltage numeric not null,

  pv1_current numeric not null,
  pv2_current numeric not null,
  pv3_current numeric not null,

  ac1_voltage numeric not null,
  ac2_voltage numeric not null,
  ac3_voltage numeric not null,

  ac1_current numeric not null,
  ac2_current numeric not null,
  ac3_current numeric not null,

  ac1_frequency numeric not null,
  ac2_frequency numeric not null,
  ac3_frequency numeric not null,

  ac1_power numeric not null,
  ac2_power numeric not null,
  ac3_power numeric not null,

  primary key (inverter, timestamp)
);
