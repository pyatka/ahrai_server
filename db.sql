CREATE TABLE employer (
    id integer NOT NULL,
    name character varying(30),
    surname character varying(30),
    en_name character varying(30),
    en_surname character varying(30)
);

CREATE SEQUENCE employer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY employer ALTER COLUMN id SET DEFAULT nextval('employer_id_seq'::regclass);
ALTER TABLE ONLY employer ADD CONSTRAINT employer_pkey PRIMARY KEY (id);

CREATE TABLE position_group (
    id integer NOT NULL,
    name character varying(30)
);

CREATE SEQUENCE position_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY position_group ALTER COLUMN id SET DEFAULT nextval('position_group_id_seq'::regclass);
ALTER TABLE ONLY position_group ADD CONSTRAINT position_group_pkey PRIMARY KEY (id);

CREATE TABLE position (
    id integer NOT NULL,
    name character varying(30),
    capacity integer,
    default_show boolean,
    position_group_id integer,
    one_position boolean
);

CREATE SEQUENCE position_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY position ALTER COLUMN id SET DEFAULT nextval('position_id_seq'::regclass);
ALTER TABLE ONLY position ADD CONSTRAINT position_pkey PRIMARY KEY (id);

CREATE INDEX position_position_group_id_idx ON position (position_group_id);

ALTER TABLE position_group ADD COLUMN view_order integer DEFAULT 0;
CREATE INDEX position_group_view_order_idx ON position_group (view_order);

ALTER TABLE position ADD COLUMN view_order integer DEFAULT 0;
CREATE INDEX position_view_order_idx ON position (view_order);

CREATE TABLE day (
    id integer NOT NULL,
    date DATE
);

CREATE SEQUENCE day_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY day ALTER COLUMN id SET DEFAULT nextval('day_id_seq'::regclass);
ALTER TABLE ONLY day ADD CONSTRAINT day_pkey PRIMARY KEY (id);
CREATE INDEX day_date_idx ON day (date);

CREATE TABLE day_to_position (
    day_id integer NOT NULL,
    position_id integer NOT NULL,
    view_order integer DEFAULT 0,
    to_show boolean DEFAULT false,
    comment character varying(50) DEFAULT NULL
);

ALTER TABLE ONLY day_to_position ADD CONSTRAINT day_to_position_pkey PRIMARY KEY (day_id, position_id);
CREATE INDEX day_to_position_view_order_idx ON day_to_position (view_order);

CREATE TABLE day_position_to_employer (
    employer_id integer NOT NULL,
    day_id integer NOT NULL,
    position_id integer NOT NULL,
    view_order integer DEFAULT 0
);

ALTER TABLE ONLY day_position_to_employer ADD CONSTRAINT day_position_to_employer_pkey PRIMARY KEY (day_id, position_id, employer_id);

ALTER TABLE position_group ADD COLUMN key_name character varying(50) DEFAULT NULL;

CREATE TABLE permission (
    id integer NOT NULL,
    code character varying(30)
);

CREATE SEQUENCE permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY permission ALTER COLUMN id SET DEFAULT nextval('permission_id_seq'::regclass);
ALTER TABLE ONLY permission ADD CONSTRAINT permission_pkey PRIMARY KEY (id);

CREATE INDEX permission_code_idx ON permission (code);

CREATE TABLE employer_group (
    id integer NOT NULL,
    code character varying(30)
);

CREATE SEQUENCE employer_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY employer_group ALTER COLUMN id SET DEFAULT nextval('employer_group_id_seq'::regclass);
ALTER TABLE ONLY employer_group ADD CONSTRAINT employer_group_pkey PRIMARY KEY (id);

CREATE INDEX employer_group_code_idx ON permission (code);

CREATE TABLE employer_group_to_permission (
    employer_group_id integer NOT NULL,
    permission_id integer NOT NULL
);

ALTER TABLE ONLY employer_group_to_permission ADD CONSTRAINT employer_group_to_permission_pkey PRIMARY KEY (employer_group_id, permission_id);

ALTER TABLE employer ADD COLUMN email character varying(50);
ALTER TABLE employer ADD COLUMN password character varying(32);

CREATE TABLE token (
    id integer NOT NULL,
    token character varying(70),
    employer_id integer not NULL,
    date timestamp DEFAULT NOW()
);

CREATE SEQUENCE token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY token ALTER COLUMN id SET DEFAULT nextval('token_id_seq'::regclass);
ALTER TABLE ONLY token ADD CONSTRAINT token_pkey PRIMARY KEY (id);

CREATE INDEX token_token_idx ON token (token);
CREATE INDEX token_employer_id_idx ON token (employer_id);

ALTER TABLE employer ADD COLUMN group_id integer DEFAULT 2;