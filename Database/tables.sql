CREATE TABLE countries (
  code CHAR(2) NOT NULL UNIQUE PRIMARY KEY, 
  name CHAR(61)
);

CREATE TABLE states (
  code CHAR(3) NOT NULL UNIQUE PRIMARY KEY, 
  name CHAR(47)
);

CREATE TABLE files (
  status_id INT NOT NULL,
  
  fileName TINYTEXT, 
  url TINYTEXT, 
  processing_date DATE, 
  md5 TINYTEXT PRIMARY KEY, 
  status TINYTEXT,

  constraint fk_state foreign key(status_id)  references status(id),
);

CREATE TABLE stations (
  country_id CHAR(2) NOT NULL,
  state_id CHAR(3) NOT NULL,

  id CHAR(11) NOT NULL UNIQUE PRIMARY KEY,
  latitude REAL,
  longitude  real,
  elevation real,
  state char(3),
  name char(30),
  gns_flag char(3),
  hcn_crn_flag char(3),
  wmo_id char(5),

  constraint fk_country foreign key(country_id)  references countries(code),
  constraint fk_state foreign key(state_id)  references states(code)
);

