CREATE TABLE pre_prod_20_gold.gold.dim_business (
business_legal_name varchar(255),
business_segment varchar(100),
business_sk varchar(10),
business_trading_name varchar(255),
PRIMARY KEY (business_sk)
);


CREATE TABLE pre_prod_20_gold.gold.dim_staff (
address_line_1 varchar(35),
address_line_2 varchar(35),
address_line_3 varchar(35),
address_line_4 varchar(35),
address_line_5 varchar(35),
agent_category_code varchar(8),
agent_category_description varchar(50),
agent_type_code tinyint,
ar_agent_type varchar(50),
business_area varchar(12),
business_development_manager varchar(50),
cf30_status varchar(100),
channel varchar(7),
competency_achieved_date date,
country varchar(35),
date_joined_partnership date,
date_left_partnership date,
dob date,
email varchar(50),
first_name varchar(60),
gender varchar(1),
gives_advice varchar(1),
is_asm varchar(50),
is_esm varchar(50),
is_principle varchar(50),
is_seller_role varchar(1),
is_supervisor varchar(50),
last_name varchar(60),
licence_number varchar(50),
mobile_telephone varchar(20),
months_active int,
nationality varchar(50),
new_experienced varchar(11),
ni_number varchar(15),
notice_given date,
panel varchar(100),
pdm varchar(100),
pdm_area varchar(100),
portal_code varchar(20),
postcode varchar(10),
recruitment_source varchar(14),
region varchar(100),
salutation varchar(35),
seller_type int,
staff_fullname varchar(255),
staff_id varchar(7),
staff_sk varchar(10),
swift_status varchar(20),
telephone_number varchar(30),
title varchar(35),
PRIMARY KEY (staff_sk)
);


CREATE TABLE pre_prod_20_gold.gold.fact_staff (
asm_sk varchar(10),
business_sk varchar(10),
date_joined_firm date,
date_left_firm date,
employment_status varchar(50),
esm_sk varchar(10),
firm_supervisor_id varchar(50),
firm_supervisor_name varchar(50),
insight_contract_status varchar(50),
job_title varchar(255),
principal_role_start_date date,
reason_for_leaving varchar(100),
staff_sk varchar(10),
supervisor_sk varchar(10),
introducer_sk varchar(10),
PRIMARY KEY (staff_sk,business_sk),
CONSTRAINT fk_1 FOREIGN KEY (staff_sk) REFERENCES dim_staff(staff_sk),
CONSTRAINT fk_2 FOREIGN KEY (business_sk) REFERENCES dim_business(business_sk),
CONSTRAINT fk_3 FOREIGN KEY (asm_sk) REFERENCES dim_staff(staff_sk),
CONSTRAINT fk_4 FOREIGN KEY (esm_sk) REFERENCES dim_staff(staff_sk),
CONSTRAINT fk_3 FOREIGN KEY (supervisor_sk) REFERENCES dim_staff(staff_sk),
CONSTRAINT fk_4 FOREIGN KEY (introducer_sk) REFERENCES dim_staff(staff_sk)
);



--ALTER TABLE pre_prod_20_gold.gold.fact_staff ADD CONSTRAINT ss1_fact_staff_dim_staff FOREIGN KEY (staff_sk) REFERENCES pre_prod_20_gold.gold.dim_staff(staff_sk);

--ALTER TABLE pre_prod_20_gold.gold.fact_staff ADD CONSTRAINT ss2_fact_staff_dim_staff FOREIGN KEY (esm_sk) REFERENCES pre_prod_20_gold.gold.dim_staff(staff_sk);

--ALTER TABLE pre_prod_20_gold.gold.fact_staff ADD CONSTRAINT ss3_fact_staff_dim_staff FOREIGN KEY (asm_sk) REFERENCES pre_prod_20_gold.gold.dim_staff(staff_sk);

--ALTER TABLE pre_prod_20_gold.gold.fact_staff ADD CONSTRAINT ss4_fact_staff_dim_staff FOREIGN KEY (supervisor_sk) REFERENCES pre_prod_20_gold.gold.dim_staff(staff_sk);

--,
--CONSTRAINT fk_1 FOREIGN KEY (asm_sk) REFERENCES dim_staff(staff_sk),
--CONSTRAINT fk_2 FOREIGN KEY (staff_sk) REFERENCES dim_staff(staff_sk)