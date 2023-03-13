--
-- PostgreSQL database dump
--

-- Dumped from database version 14.7 (Ubuntu 14.7-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.7 (Ubuntu 14.7-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: inventory; Type: TABLE; Schema: public; Owner: xyzdbm
--

CREATE TABLE public.inventory (
    rp_id integer NOT NULL,
    prod_id integer NOT NULL,
    price double precision NOT NULL,
    quantity integer NOT NULL
);


ALTER TABLE public.inventory OWNER TO xyzdbm;

--
-- Name: products; Type: TABLE; Schema: public; Owner: xyzdbm
--

CREATE TABLE public.products (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    descr character varying(100) NOT NULL
);


ALTER TABLE public.products OWNER TO xyzdbm;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: xyzdbm
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO xyzdbm;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xyzdbm
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: retail_points; Type: TABLE; Schema: public; Owner: xyzdbm
--

CREATE TABLE public.retail_points (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.retail_points OWNER TO xyzdbm;

--
-- Name: retail_points_id_seq; Type: SEQUENCE; Schema: public; Owner: xyzdbm
--

CREATE SEQUENCE public.retail_points_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.retail_points_id_seq OWNER TO xyzdbm;

--
-- Name: retail_points_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: xyzdbm
--

ALTER SEQUENCE public.retail_points_id_seq OWNED BY public.retail_points.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: xyzdbm
--

CREATE TABLE public.users (
    id character varying(10) NOT NULL,
    names character varying(40) NOT NULL,
    lastnames character varying(40) NOT NULL,
    email character varying(40) NOT NULL,
    password character varying(110) NOT NULL,
    role character varying(4) NOT NULL,
    rp_id integer NOT NULL
);


ALTER TABLE public.users OWNER TO xyzdbm;

--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: retail_points id; Type: DEFAULT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.retail_points ALTER COLUMN id SET DEFAULT nextval('public.retail_points_id_seq'::regclass);


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: xyzdbm
--

COPY public.inventory (rp_id, prod_id, price, quantity) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: xyzdbm
--

COPY public.products (id, name, descr) FROM stdin;
\.


--
-- Data for Name: retail_points; Type: TABLE DATA; Schema: public; Owner: xyzdbm
--

COPY public.retail_points (id, name) FROM stdin;
1       HQ
2       RP1
3       RP2
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: xyzdbm
--

COPY public.users (id, names, lastnames, email, password, role, rp_id) FROM stdin;
1000939903      Juan Fernando   Plata Quintero  juanfernandoplata@hotmail.com   pbkdf2:sha256:260000$TbyzLnwe2JPhDdv0$f5b236f8d5e8880200883ad96332eb74f8a17cba8cbc5da6baeae90a7779f03c      DIR     1
\.


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xyzdbm
--

SELECT pg_catalog.setval('public.products_id_seq', 1, false);


--
-- Name: retail_points_id_seq; Type: SEQUENCE SET; Schema: public; Owner: xyzdbm
--

SELECT pg_catalog.setval('public.retail_points_id_seq', 3, true);


--
-- Name: inventory inventory_pk; Type: CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pk PRIMARY KEY (rp_id, prod_id);


--
-- Name: products products_name_key; Type: CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_name_key UNIQUE (name);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: retail_points retail_points_pkey; Type: CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.retail_points
    ADD CONSTRAINT retail_points_pkey PRIMARY KEY (id);


--
-- Name: users users_pk; Type: CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);


--
-- Name: inventory prod_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT prod_id_fk FOREIGN KEY (prod_id) REFERENCES public.products(id);


--
-- Name: inventory rp_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: xyzdbm
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT rp_id_fk FOREIGN KEY (rp_id) REFERENCES public.retail_points(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

GRANT ALL ON SCHEMA public TO xyzdbm;

--
-- DEFAULT DB DATA SET UP (INSERTS)
--

insert into public.retail_points values(1, 'HQ');
insert into public.retail_points values(2, 'RP1');
insert into public.retail_points values(3, 'RP2');

insert into public.users values('1', 'DIRECTOR', 'XYZ', 'dir@xyz.com', 'pbkdf2:sha256:260000$paBnOsNAb7zdM5NX$d8784dec317431f0cf2a373482abd39370df8c1c7bcf262f97058cefd3c3631e', 'DIR', 1);

--
-- PostgreSQL database dump complete
--

