--
-- PostgreSQL database dump
--

\restrict YHc7ycNiYlEjO7M3fmy9eNhRNKjTnZeAfcbCdv9RQUnhoozS54GERtqeqpOStMH

-- Dumped from database version 17.12
-- Dumped by pg_dump version 17.12

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: demand_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.demand_history (
    demand_id integer NOT NULL,
    product_id integer NOT NULL,
    retailer_id integer NOT NULL,
    demand_date date NOT NULL,
    quantity_sold integer NOT NULL,
    CONSTRAINT ck_demand_quantity_nonnegative CHECK ((quantity_sold >= 0))
);


--
-- Name: demand_history_demand_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.demand_history_demand_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: demand_history_demand_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.demand_history_demand_id_seq OWNED BY public.demand_history.demand_id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory (
    inventory_id integer NOT NULL,
    product_id integer NOT NULL,
    warehouse_id integer,
    retailer_id integer,
    quantity integer NOT NULL,
    reorder_point integer NOT NULL,
    safety_stock integer NOT NULL,
    CONSTRAINT ck_inventory_quantity_nonnegative CHECK ((quantity >= 0)),
    CONSTRAINT ck_inventory_reorder_nonnegative CHECK ((reorder_point >= 0)),
    CONSTRAINT ck_inventory_safety_nonnegative CHECK ((safety_stock >= 0)),
    CONSTRAINT ck_inventory_single_location CHECK ((((warehouse_id IS NOT NULL) AND (retailer_id IS NULL)) OR ((warehouse_id IS NULL) AND (retailer_id IS NOT NULL))))
);


--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventory_inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventory_inventory_id_seq OWNED BY public.inventory.inventory_id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    source_type character varying(20) NOT NULL,
    source_id integer NOT NULL,
    destination_type character varying(20) NOT NULL,
    destination_id integer NOT NULL,
    quantity integer NOT NULL,
    order_date date NOT NULL,
    expected_delivery_date date NOT NULL,
    status character varying(30) NOT NULL,
    CONSTRAINT ck_order_delivery_date CHECK ((expected_delivery_date >= order_date)),
    CONSTRAINT ck_order_destination_type CHECK (((destination_type)::text = ANY ((ARRAY['warehouse'::character varying, 'retailer'::character varying])::text[]))),
    CONSTRAINT ck_order_location_ids CHECK (((source_id > 0) AND (destination_id > 0))),
    CONSTRAINT ck_order_quantity_positive CHECK ((quantity > 0)),
    CONSTRAINT ck_order_source_type CHECK (((source_type)::text = ANY ((ARRAY['supplier'::character varying, 'warehouse'::character varying])::text[]))),
    CONSTRAINT ck_order_status CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'shipped'::character varying, 'delivered'::character varying, 'cancelled'::character varying])::text[])))
);


--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orders_order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orders_order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orders_order_id_seq OWNED BY public.orders.order_id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_name character varying(100) NOT NULL,
    category character varying(100) NOT NULL,
    unit_price double precision NOT NULL,
    supplier_id integer NOT NULL,
    CONSTRAINT ck_product_price_nonnegative CHECK ((unit_price >= (0)::double precision))
);


--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: retailers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.retailers (
    retailer_id integer NOT NULL,
    retailer_name character varying(100) NOT NULL,
    location character varying(150) NOT NULL
);


--
-- Name: retailers_retailer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.retailers_retailer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: retailers_retailer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.retailers_retailer_id_seq OWNED BY public.retailers.retailer_id;


--
-- Name: shipments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shipments (
    shipment_id integer NOT NULL,
    order_id integer NOT NULL,
    shipped_date date NOT NULL,
    expected_arrival_date date NOT NULL,
    actual_arrival_date date,
    status character varying(30) NOT NULL,
    CONSTRAINT ck_shipment_actual_arrival CHECK (((actual_arrival_date IS NULL) OR (actual_arrival_date >= shipped_date))),
    CONSTRAINT ck_shipment_expected_arrival CHECK ((expected_arrival_date >= shipped_date)),
    CONSTRAINT ck_shipment_status CHECK (((status)::text = ANY ((ARRAY['in_transit'::character varying, 'delivered'::character varying, 'delayed'::character varying, 'cancelled'::character varying])::text[])))
);


--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.shipments_shipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.shipments_shipment_id_seq OWNED BY public.shipments.shipment_id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    supplier_name character varying(100) NOT NULL,
    location character varying(150) NOT NULL,
    average_lead_time_days integer NOT NULL,
    reliability_score double precision NOT NULL,
    CONSTRAINT ck_supplier_lead_time_nonnegative CHECK ((average_lead_time_days >= 0)),
    CONSTRAINT ck_supplier_reliability_range CHECK (((reliability_score >= (0)::double precision) AND (reliability_score <= (1)::double precision)))
);


--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.suppliers_supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.suppliers_supplier_id_seq OWNED BY public.suppliers.supplier_id;


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.warehouses (
    warehouse_id integer NOT NULL,
    warehouse_name character varying(100) NOT NULL,
    location character varying(150) NOT NULL,
    capacity integer NOT NULL,
    CONSTRAINT ck_warehouse_capacity_nonnegative CHECK ((capacity >= 0))
);


--
-- Name: warehouses_warehouse_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.warehouses_warehouse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: warehouses_warehouse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.warehouses_warehouse_id_seq OWNED BY public.warehouses.warehouse_id;


--
-- Name: demand_history demand_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demand_history ALTER COLUMN demand_id SET DEFAULT nextval('public.demand_history_demand_id_seq'::regclass);


--
-- Name: inventory inventory_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory ALTER COLUMN inventory_id SET DEFAULT nextval('public.inventory_inventory_id_seq'::regclass);


--
-- Name: orders order_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders ALTER COLUMN order_id SET DEFAULT nextval('public.orders_order_id_seq'::regclass);


--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: retailers retailer_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.retailers ALTER COLUMN retailer_id SET DEFAULT nextval('public.retailers_retailer_id_seq'::regclass);


--
-- Name: shipments shipment_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shipments ALTER COLUMN shipment_id SET DEFAULT nextval('public.shipments_shipment_id_seq'::regclass);


--
-- Name: suppliers supplier_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('public.suppliers_supplier_id_seq'::regclass);


--
-- Name: warehouses warehouse_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses ALTER COLUMN warehouse_id SET DEFAULT nextval('public.warehouses_warehouse_id_seq'::regclass);


--
-- Data for Name: demand_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.demand_history (demand_id, product_id, retailer_id, demand_date, quantity_sold) FROM stdin;
1	1	1	2026-01-01	15
2	1	1	2026-01-02	16
3	1	1	2026-01-03	17
4	1	1	2026-01-04	18
5	1	1	2026-01-05	19
6	1	1	2026-01-06	20
7	1	1	2026-01-07	21
8	1	1	2026-01-08	15
9	1	1	2026-01-09	16
10	1	1	2026-01-10	17
11	1	1	2026-01-11	18
12	1	1	2026-01-12	19
13	1	1	2026-01-13	20
14	1	1	2026-01-14	21
15	1	1	2026-01-15	15
16	1	1	2026-01-16	16
17	1	1	2026-01-17	17
18	1	1	2026-01-18	18
19	1	1	2026-01-19	19
20	1	1	2026-01-20	20
21	1	1	2026-01-21	21
22	1	1	2026-01-22	15
23	1	1	2026-01-23	16
24	1	1	2026-01-24	17
25	1	1	2026-01-25	18
26	1	1	2026-01-26	19
27	1	1	2026-01-27	20
28	1	1	2026-01-28	21
29	1	1	2026-01-29	15
30	1	1	2026-01-30	16
31	1	1	2026-01-31	17
32	1	1	2026-02-01	18
33	1	1	2026-02-02	19
34	1	1	2026-02-03	20
35	1	1	2026-02-04	21
36	1	1	2026-02-05	15
37	1	1	2026-02-06	16
38	1	1	2026-02-07	17
39	1	1	2026-02-08	18
40	1	1	2026-02-09	19
41	1	1	2026-02-10	20
42	1	1	2026-02-11	21
43	1	1	2026-02-12	15
44	1	1	2026-02-13	16
45	1	1	2026-02-14	17
46	1	1	2026-02-15	18
47	1	1	2026-02-16	19
48	1	1	2026-02-17	20
49	1	1	2026-02-18	21
50	1	1	2026-02-19	15
51	1	1	2026-02-20	16
52	1	1	2026-02-21	17
53	1	1	2026-02-22	18
54	1	1	2026-02-23	19
55	1	1	2026-02-24	20
56	1	1	2026-02-25	21
57	1	1	2026-02-26	15
58	1	1	2026-02-27	16
59	1	1	2026-02-28	17
60	1	1	2026-03-01	18
61	1	1	2026-03-02	19
62	1	1	2026-03-03	20
63	1	1	2026-03-04	21
64	1	1	2026-03-05	15
65	1	1	2026-03-06	16
66	1	1	2026-03-07	17
67	1	1	2026-03-08	18
68	1	1	2026-03-09	19
69	1	1	2026-03-10	20
70	1	1	2026-03-11	21
71	1	1	2026-03-12	15
72	1	1	2026-03-13	16
73	1	1	2026-03-14	17
74	1	1	2026-03-15	18
75	1	1	2026-03-16	19
76	1	1	2026-03-17	20
77	1	1	2026-03-18	21
78	1	1	2026-03-19	15
79	1	1	2026-03-20	16
80	1	1	2026-03-21	17
81	1	1	2026-03-22	18
82	1	1	2026-03-23	19
83	1	1	2026-03-24	20
84	1	1	2026-03-25	21
85	1	1	2026-03-26	15
86	1	1	2026-03-27	16
87	1	1	2026-03-28	17
88	1	1	2026-03-29	18
89	1	1	2026-03-30	19
90	1	1	2026-03-31	20
91	1	2	2026-01-01	17
92	1	2	2026-01-02	18
93	1	2	2026-01-03	19
94	1	2	2026-01-04	20
95	1	2	2026-01-05	21
96	1	2	2026-01-06	22
97	1	2	2026-01-07	23
98	1	2	2026-01-08	17
99	1	2	2026-01-09	18
100	1	2	2026-01-10	19
101	1	2	2026-01-11	20
102	1	2	2026-01-12	21
103	1	2	2026-01-13	22
104	1	2	2026-01-14	23
105	1	2	2026-01-15	17
106	1	2	2026-01-16	18
107	1	2	2026-01-17	19
108	1	2	2026-01-18	20
109	1	2	2026-01-19	21
110	1	2	2026-01-20	22
111	1	2	2026-01-21	23
112	1	2	2026-01-22	17
113	1	2	2026-01-23	18
114	1	2	2026-01-24	19
115	1	2	2026-01-25	20
116	1	2	2026-01-26	21
117	1	2	2026-01-27	22
118	1	2	2026-01-28	23
119	1	2	2026-01-29	17
120	1	2	2026-01-30	18
121	1	2	2026-01-31	19
122	1	2	2026-02-01	20
123	1	2	2026-02-02	21
124	1	2	2026-02-03	22
125	1	2	2026-02-04	23
126	1	2	2026-02-05	17
127	1	2	2026-02-06	18
128	1	2	2026-02-07	19
129	1	2	2026-02-08	20
130	1	2	2026-02-09	21
131	1	2	2026-02-10	22
132	1	2	2026-02-11	23
133	1	2	2026-02-12	17
134	1	2	2026-02-13	18
135	1	2	2026-02-14	19
136	1	2	2026-02-15	20
137	1	2	2026-02-16	21
138	1	2	2026-02-17	22
139	1	2	2026-02-18	23
140	1	2	2026-02-19	17
141	1	2	2026-02-20	18
142	1	2	2026-02-21	19
143	1	2	2026-02-22	20
144	1	2	2026-02-23	21
145	1	2	2026-02-24	22
146	1	2	2026-02-25	23
147	1	2	2026-02-26	17
148	1	2	2026-02-27	18
149	1	2	2026-02-28	19
150	1	2	2026-03-01	20
151	1	2	2026-03-02	21
152	1	2	2026-03-03	22
153	1	2	2026-03-04	23
154	1	2	2026-03-05	17
155	1	2	2026-03-06	18
156	1	2	2026-03-07	19
157	1	2	2026-03-08	20
158	1	2	2026-03-09	21
159	1	2	2026-03-10	22
160	1	2	2026-03-11	23
161	1	2	2026-03-12	17
162	1	2	2026-03-13	18
163	1	2	2026-03-14	19
164	1	2	2026-03-15	20
165	1	2	2026-03-16	21
166	1	2	2026-03-17	22
167	1	2	2026-03-18	23
168	1	2	2026-03-19	17
169	1	2	2026-03-20	18
170	1	2	2026-03-21	19
171	1	2	2026-03-22	20
172	1	2	2026-03-23	21
173	1	2	2026-03-24	22
174	1	2	2026-03-25	23
175	1	2	2026-03-26	17
176	1	2	2026-03-27	18
177	1	2	2026-03-28	19
178	1	2	2026-03-29	20
179	1	2	2026-03-30	21
180	1	2	2026-03-31	22
181	1	3	2026-01-01	19
182	1	3	2026-01-02	20
183	1	3	2026-01-03	21
184	1	3	2026-01-04	22
185	1	3	2026-01-05	23
186	1	3	2026-01-06	24
187	1	3	2026-01-07	25
188	1	3	2026-01-08	19
189	1	3	2026-01-09	20
190	1	3	2026-01-10	21
191	1	3	2026-01-11	22
192	1	3	2026-01-12	23
193	1	3	2026-01-13	24
194	1	3	2026-01-14	25
195	1	3	2026-01-15	19
196	1	3	2026-01-16	20
197	1	3	2026-01-17	21
198	1	3	2026-01-18	22
199	1	3	2026-01-19	23
200	1	3	2026-01-20	24
201	1	3	2026-01-21	25
202	1	3	2026-01-22	19
203	1	3	2026-01-23	20
204	1	3	2026-01-24	21
205	1	3	2026-01-25	22
206	1	3	2026-01-26	23
207	1	3	2026-01-27	24
208	1	3	2026-01-28	25
209	1	3	2026-01-29	19
210	1	3	2026-01-30	20
211	1	3	2026-01-31	21
212	1	3	2026-02-01	22
213	1	3	2026-02-02	23
214	1	3	2026-02-03	24
215	1	3	2026-02-04	25
216	1	3	2026-02-05	19
217	1	3	2026-02-06	20
218	1	3	2026-02-07	21
219	1	3	2026-02-08	22
220	1	3	2026-02-09	23
221	1	3	2026-02-10	24
222	1	3	2026-02-11	25
223	1	3	2026-02-12	19
224	1	3	2026-02-13	20
225	1	3	2026-02-14	21
226	1	3	2026-02-15	22
227	1	3	2026-02-16	23
228	1	3	2026-02-17	24
229	1	3	2026-02-18	25
230	1	3	2026-02-19	19
231	1	3	2026-02-20	20
232	1	3	2026-02-21	21
233	1	3	2026-02-22	22
234	1	3	2026-02-23	23
235	1	3	2026-02-24	24
236	1	3	2026-02-25	25
237	1	3	2026-02-26	19
238	1	3	2026-02-27	20
239	1	3	2026-02-28	21
240	1	3	2026-03-01	22
241	1	3	2026-03-02	23
242	1	3	2026-03-03	24
243	1	3	2026-03-04	25
244	1	3	2026-03-05	19
245	1	3	2026-03-06	20
246	1	3	2026-03-07	21
247	1	3	2026-03-08	22
248	1	3	2026-03-09	23
249	1	3	2026-03-10	24
250	1	3	2026-03-11	25
251	1	3	2026-03-12	19
252	1	3	2026-03-13	20
253	1	3	2026-03-14	21
254	1	3	2026-03-15	22
255	1	3	2026-03-16	23
256	1	3	2026-03-17	24
257	1	3	2026-03-18	25
258	1	3	2026-03-19	19
259	1	3	2026-03-20	20
260	1	3	2026-03-21	21
261	1	3	2026-03-22	22
262	1	3	2026-03-23	23
263	1	3	2026-03-24	24
264	1	3	2026-03-25	25
265	1	3	2026-03-26	19
266	1	3	2026-03-27	20
267	1	3	2026-03-28	21
268	1	3	2026-03-29	22
269	1	3	2026-03-30	23
270	1	3	2026-03-31	24
271	2	1	2026-01-01	18
272	2	1	2026-01-02	19
273	2	1	2026-01-03	20
274	2	1	2026-01-04	21
275	2	1	2026-01-05	22
276	2	1	2026-01-06	23
277	2	1	2026-01-07	24
278	2	1	2026-01-08	18
279	2	1	2026-01-09	19
280	2	1	2026-01-10	20
281	2	1	2026-01-11	21
282	2	1	2026-01-12	22
283	2	1	2026-01-13	23
284	2	1	2026-01-14	24
285	2	1	2026-01-15	18
286	2	1	2026-01-16	19
287	2	1	2026-01-17	20
288	2	1	2026-01-18	21
289	2	1	2026-01-19	22
290	2	1	2026-01-20	23
291	2	1	2026-01-21	24
292	2	1	2026-01-22	18
293	2	1	2026-01-23	19
294	2	1	2026-01-24	20
295	2	1	2026-01-25	21
296	2	1	2026-01-26	22
297	2	1	2026-01-27	23
298	2	1	2026-01-28	24
299	2	1	2026-01-29	18
300	2	1	2026-01-30	19
301	2	1	2026-01-31	20
302	2	1	2026-02-01	21
303	2	1	2026-02-02	22
304	2	1	2026-02-03	23
305	2	1	2026-02-04	24
306	2	1	2026-02-05	18
307	2	1	2026-02-06	19
308	2	1	2026-02-07	20
309	2	1	2026-02-08	21
310	2	1	2026-02-09	22
311	2	1	2026-02-10	23
312	2	1	2026-02-11	24
313	2	1	2026-02-12	18
314	2	1	2026-02-13	19
315	2	1	2026-02-14	20
316	2	1	2026-02-15	21
317	2	1	2026-02-16	22
318	2	1	2026-02-17	23
319	2	1	2026-02-18	24
320	2	1	2026-02-19	18
321	2	1	2026-02-20	19
322	2	1	2026-02-21	20
323	2	1	2026-02-22	21
324	2	1	2026-02-23	22
325	2	1	2026-02-24	23
326	2	1	2026-02-25	24
327	2	1	2026-02-26	18
328	2	1	2026-02-27	19
329	2	1	2026-02-28	20
330	2	1	2026-03-01	21
331	2	1	2026-03-02	22
332	2	1	2026-03-03	23
333	2	1	2026-03-04	24
334	2	1	2026-03-05	18
335	2	1	2026-03-06	19
336	2	1	2026-03-07	20
337	2	1	2026-03-08	21
338	2	1	2026-03-09	22
339	2	1	2026-03-10	23
340	2	1	2026-03-11	24
341	2	1	2026-03-12	18
342	2	1	2026-03-13	19
343	2	1	2026-03-14	20
344	2	1	2026-03-15	21
345	2	1	2026-03-16	22
346	2	1	2026-03-17	23
347	2	1	2026-03-18	24
348	2	1	2026-03-19	18
349	2	1	2026-03-20	19
350	2	1	2026-03-21	20
351	2	1	2026-03-22	21
352	2	1	2026-03-23	22
353	2	1	2026-03-24	23
354	2	1	2026-03-25	24
355	2	1	2026-03-26	18
356	2	1	2026-03-27	19
357	2	1	2026-03-28	20
358	2	1	2026-03-29	21
359	2	1	2026-03-30	22
360	2	1	2026-03-31	23
361	2	2	2026-01-01	20
362	2	2	2026-01-02	21
363	2	2	2026-01-03	22
364	2	2	2026-01-04	23
365	2	2	2026-01-05	24
366	2	2	2026-01-06	25
367	2	2	2026-01-07	10
368	2	2	2026-01-08	20
369	2	2	2026-01-09	21
370	2	2	2026-01-10	22
371	2	2	2026-01-11	23
372	2	2	2026-01-12	24
373	2	2	2026-01-13	25
374	2	2	2026-01-14	10
375	2	2	2026-01-15	20
376	2	2	2026-01-16	21
377	2	2	2026-01-17	22
378	2	2	2026-01-18	23
379	2	2	2026-01-19	24
380	2	2	2026-01-20	25
381	2	2	2026-01-21	10
382	2	2	2026-01-22	20
383	2	2	2026-01-23	21
384	2	2	2026-01-24	22
385	2	2	2026-01-25	23
386	2	2	2026-01-26	24
387	2	2	2026-01-27	25
388	2	2	2026-01-28	10
389	2	2	2026-01-29	20
390	2	2	2026-01-30	21
391	2	2	2026-01-31	22
392	2	2	2026-02-01	23
393	2	2	2026-02-02	24
394	2	2	2026-02-03	25
395	2	2	2026-02-04	10
396	2	2	2026-02-05	20
397	2	2	2026-02-06	21
398	2	2	2026-02-07	22
399	2	2	2026-02-08	23
400	2	2	2026-02-09	24
401	2	2	2026-02-10	25
402	2	2	2026-02-11	10
403	2	2	2026-02-12	20
404	2	2	2026-02-13	21
405	2	2	2026-02-14	22
406	2	2	2026-02-15	23
407	2	2	2026-02-16	24
408	2	2	2026-02-17	25
409	2	2	2026-02-18	10
410	2	2	2026-02-19	20
411	2	2	2026-02-20	21
412	2	2	2026-02-21	22
413	2	2	2026-02-22	23
414	2	2	2026-02-23	24
415	2	2	2026-02-24	25
416	2	2	2026-02-25	10
417	2	2	2026-02-26	20
418	2	2	2026-02-27	21
419	2	2	2026-02-28	22
420	2	2	2026-03-01	23
421	2	2	2026-03-02	24
422	2	2	2026-03-03	25
423	2	2	2026-03-04	10
424	2	2	2026-03-05	20
425	2	2	2026-03-06	21
426	2	2	2026-03-07	22
427	2	2	2026-03-08	23
428	2	2	2026-03-09	24
429	2	2	2026-03-10	25
430	2	2	2026-03-11	10
431	2	2	2026-03-12	20
432	2	2	2026-03-13	21
433	2	2	2026-03-14	22
434	2	2	2026-03-15	23
435	2	2	2026-03-16	24
436	2	2	2026-03-17	25
437	2	2	2026-03-18	10
438	2	2	2026-03-19	20
439	2	2	2026-03-20	21
440	2	2	2026-03-21	22
441	2	2	2026-03-22	23
442	2	2	2026-03-23	24
443	2	2	2026-03-24	25
444	2	2	2026-03-25	10
445	2	2	2026-03-26	20
446	2	2	2026-03-27	21
447	2	2	2026-03-28	22
448	2	2	2026-03-29	23
449	2	2	2026-03-30	24
450	2	2	2026-03-31	25
451	2	3	2026-01-01	22
452	2	3	2026-01-02	23
453	2	3	2026-01-03	24
454	2	3	2026-01-04	25
455	2	3	2026-01-05	10
456	2	3	2026-01-06	11
457	2	3	2026-01-07	12
458	2	3	2026-01-08	22
459	2	3	2026-01-09	23
460	2	3	2026-01-10	24
461	2	3	2026-01-11	25
462	2	3	2026-01-12	10
463	2	3	2026-01-13	11
464	2	3	2026-01-14	12
465	2	3	2026-01-15	22
466	2	3	2026-01-16	23
467	2	3	2026-01-17	24
468	2	3	2026-01-18	25
469	2	3	2026-01-19	10
470	2	3	2026-01-20	11
471	2	3	2026-01-21	12
472	2	3	2026-01-22	22
473	2	3	2026-01-23	23
474	2	3	2026-01-24	24
475	2	3	2026-01-25	25
476	2	3	2026-01-26	10
477	2	3	2026-01-27	11
478	2	3	2026-01-28	12
479	2	3	2026-01-29	22
480	2	3	2026-01-30	23
481	2	3	2026-01-31	24
482	2	3	2026-02-01	25
483	2	3	2026-02-02	10
484	2	3	2026-02-03	11
485	2	3	2026-02-04	12
486	2	3	2026-02-05	22
487	2	3	2026-02-06	23
488	2	3	2026-02-07	24
489	2	3	2026-02-08	25
490	2	3	2026-02-09	10
491	2	3	2026-02-10	11
492	2	3	2026-02-11	12
493	2	3	2026-02-12	22
494	2	3	2026-02-13	23
495	2	3	2026-02-14	24
496	2	3	2026-02-15	25
497	2	3	2026-02-16	10
498	2	3	2026-02-17	11
499	2	3	2026-02-18	12
500	2	3	2026-02-19	22
501	2	3	2026-02-20	23
502	2	3	2026-02-21	24
503	2	3	2026-02-22	25
504	2	3	2026-02-23	10
505	2	3	2026-02-24	11
506	2	3	2026-02-25	12
507	2	3	2026-02-26	22
508	2	3	2026-02-27	23
509	2	3	2026-02-28	24
510	2	3	2026-03-01	25
511	2	3	2026-03-02	10
512	2	3	2026-03-03	11
513	2	3	2026-03-04	12
514	2	3	2026-03-05	22
515	2	3	2026-03-06	23
516	2	3	2026-03-07	24
517	2	3	2026-03-08	25
518	2	3	2026-03-09	10
519	2	3	2026-03-10	11
520	2	3	2026-03-11	12
521	2	3	2026-03-12	22
522	2	3	2026-03-13	23
523	2	3	2026-03-14	24
524	2	3	2026-03-15	25
525	2	3	2026-03-16	10
526	2	3	2026-03-17	11
527	2	3	2026-03-18	12
528	2	3	2026-03-19	22
529	2	3	2026-03-20	23
530	2	3	2026-03-21	24
531	2	3	2026-03-22	25
532	2	3	2026-03-23	10
533	2	3	2026-03-24	11
534	2	3	2026-03-25	12
535	2	3	2026-03-26	22
536	2	3	2026-03-27	23
537	2	3	2026-03-28	24
538	2	3	2026-03-29	25
539	2	3	2026-03-30	10
540	2	3	2026-03-31	11
541	3	1	2026-01-01	21
542	3	1	2026-01-02	22
543	3	1	2026-01-03	23
544	3	1	2026-01-04	24
545	3	1	2026-01-05	25
546	3	1	2026-01-06	10
547	3	1	2026-01-07	11
548	3	1	2026-01-08	21
549	3	1	2026-01-09	22
550	3	1	2026-01-10	23
551	3	1	2026-01-11	24
552	3	1	2026-01-12	25
553	3	1	2026-01-13	10
554	3	1	2026-01-14	11
555	3	1	2026-01-15	21
556	3	1	2026-01-16	22
557	3	1	2026-01-17	23
558	3	1	2026-01-18	24
559	3	1	2026-01-19	25
560	3	1	2026-01-20	10
561	3	1	2026-01-21	11
562	3	1	2026-01-22	21
563	3	1	2026-01-23	22
564	3	1	2026-01-24	23
565	3	1	2026-01-25	24
566	3	1	2026-01-26	25
567	3	1	2026-01-27	10
568	3	1	2026-01-28	11
569	3	1	2026-01-29	21
570	3	1	2026-01-30	22
571	3	1	2026-01-31	23
572	3	1	2026-02-01	24
573	3	1	2026-02-02	25
574	3	1	2026-02-03	10
575	3	1	2026-02-04	11
576	3	1	2026-02-05	21
577	3	1	2026-02-06	22
578	3	1	2026-02-07	23
579	3	1	2026-02-08	24
580	3	1	2026-02-09	25
581	3	1	2026-02-10	10
582	3	1	2026-02-11	11
583	3	1	2026-02-12	21
584	3	1	2026-02-13	22
585	3	1	2026-02-14	23
586	3	1	2026-02-15	24
587	3	1	2026-02-16	25
588	3	1	2026-02-17	10
589	3	1	2026-02-18	11
590	3	1	2026-02-19	21
591	3	1	2026-02-20	22
592	3	1	2026-02-21	23
593	3	1	2026-02-22	24
594	3	1	2026-02-23	25
595	3	1	2026-02-24	10
596	3	1	2026-02-25	11
597	3	1	2026-02-26	21
598	3	1	2026-02-27	22
599	3	1	2026-02-28	23
600	3	1	2026-03-01	24
601	3	1	2026-03-02	25
602	3	1	2026-03-03	10
603	3	1	2026-03-04	11
604	3	1	2026-03-05	21
605	3	1	2026-03-06	22
606	3	1	2026-03-07	23
607	3	1	2026-03-08	24
608	3	1	2026-03-09	25
609	3	1	2026-03-10	10
610	3	1	2026-03-11	11
611	3	1	2026-03-12	21
612	3	1	2026-03-13	22
613	3	1	2026-03-14	23
614	3	1	2026-03-15	24
615	3	1	2026-03-16	25
616	3	1	2026-03-17	10
617	3	1	2026-03-18	11
618	3	1	2026-03-19	21
619	3	1	2026-03-20	22
620	3	1	2026-03-21	23
621	3	1	2026-03-22	24
622	3	1	2026-03-23	25
623	3	1	2026-03-24	10
624	3	1	2026-03-25	11
625	3	1	2026-03-26	21
626	3	1	2026-03-27	22
627	3	1	2026-03-28	23
628	3	1	2026-03-29	24
629	3	1	2026-03-30	25
630	3	1	2026-03-31	10
631	3	2	2026-01-01	23
632	3	2	2026-01-02	24
633	3	2	2026-01-03	25
634	3	2	2026-01-04	10
635	3	2	2026-01-05	11
636	3	2	2026-01-06	12
637	3	2	2026-01-07	13
638	3	2	2026-01-08	23
639	3	2	2026-01-09	24
640	3	2	2026-01-10	25
641	3	2	2026-01-11	10
642	3	2	2026-01-12	11
643	3	2	2026-01-13	12
644	3	2	2026-01-14	13
645	3	2	2026-01-15	23
646	3	2	2026-01-16	24
647	3	2	2026-01-17	25
648	3	2	2026-01-18	10
649	3	2	2026-01-19	11
650	3	2	2026-01-20	12
651	3	2	2026-01-21	13
652	3	2	2026-01-22	23
653	3	2	2026-01-23	24
654	3	2	2026-01-24	25
655	3	2	2026-01-25	10
656	3	2	2026-01-26	11
657	3	2	2026-01-27	12
658	3	2	2026-01-28	13
659	3	2	2026-01-29	23
660	3	2	2026-01-30	24
661	3	2	2026-01-31	25
662	3	2	2026-02-01	10
663	3	2	2026-02-02	11
664	3	2	2026-02-03	12
665	3	2	2026-02-04	13
666	3	2	2026-02-05	23
667	3	2	2026-02-06	24
668	3	2	2026-02-07	25
669	3	2	2026-02-08	10
670	3	2	2026-02-09	11
671	3	2	2026-02-10	12
672	3	2	2026-02-11	13
673	3	2	2026-02-12	23
674	3	2	2026-02-13	24
675	3	2	2026-02-14	25
676	3	2	2026-02-15	10
677	3	2	2026-02-16	11
678	3	2	2026-02-17	12
679	3	2	2026-02-18	13
680	3	2	2026-02-19	23
681	3	2	2026-02-20	24
682	3	2	2026-02-21	25
683	3	2	2026-02-22	10
684	3	2	2026-02-23	11
685	3	2	2026-02-24	12
686	3	2	2026-02-25	13
687	3	2	2026-02-26	23
688	3	2	2026-02-27	24
689	3	2	2026-02-28	25
690	3	2	2026-03-01	10
691	3	2	2026-03-02	11
692	3	2	2026-03-03	12
693	3	2	2026-03-04	13
694	3	2	2026-03-05	23
695	3	2	2026-03-06	24
696	3	2	2026-03-07	25
697	3	2	2026-03-08	10
698	3	2	2026-03-09	11
699	3	2	2026-03-10	12
700	3	2	2026-03-11	13
701	3	2	2026-03-12	23
702	3	2	2026-03-13	24
703	3	2	2026-03-14	25
704	3	2	2026-03-15	10
705	3	2	2026-03-16	11
706	3	2	2026-03-17	12
707	3	2	2026-03-18	13
708	3	2	2026-03-19	23
709	3	2	2026-03-20	24
710	3	2	2026-03-21	25
711	3	2	2026-03-22	10
712	3	2	2026-03-23	11
713	3	2	2026-03-24	12
714	3	2	2026-03-25	13
715	3	2	2026-03-26	23
716	3	2	2026-03-27	24
717	3	2	2026-03-28	25
718	3	2	2026-03-29	10
719	3	2	2026-03-30	11
720	3	2	2026-03-31	12
721	3	3	2026-01-01	25
722	3	3	2026-01-02	10
723	3	3	2026-01-03	11
724	3	3	2026-01-04	12
725	3	3	2026-01-05	13
726	3	3	2026-01-06	14
727	3	3	2026-01-07	15
728	3	3	2026-01-08	25
729	3	3	2026-01-09	10
730	3	3	2026-01-10	11
731	3	3	2026-01-11	12
732	3	3	2026-01-12	13
733	3	3	2026-01-13	14
734	3	3	2026-01-14	15
735	3	3	2026-01-15	25
736	3	3	2026-01-16	10
737	3	3	2026-01-17	11
738	3	3	2026-01-18	12
739	3	3	2026-01-19	13
740	3	3	2026-01-20	14
741	3	3	2026-01-21	15
742	3	3	2026-01-22	25
743	3	3	2026-01-23	10
744	3	3	2026-01-24	11
745	3	3	2026-01-25	12
746	3	3	2026-01-26	13
747	3	3	2026-01-27	14
748	3	3	2026-01-28	15
749	3	3	2026-01-29	25
750	3	3	2026-01-30	10
751	3	3	2026-01-31	11
752	3	3	2026-02-01	12
753	3	3	2026-02-02	13
754	3	3	2026-02-03	14
755	3	3	2026-02-04	15
756	3	3	2026-02-05	25
757	3	3	2026-02-06	10
758	3	3	2026-02-07	11
759	3	3	2026-02-08	12
760	3	3	2026-02-09	13
761	3	3	2026-02-10	14
762	3	3	2026-02-11	15
763	3	3	2026-02-12	25
764	3	3	2026-02-13	10
765	3	3	2026-02-14	11
766	3	3	2026-02-15	12
767	3	3	2026-02-16	13
768	3	3	2026-02-17	14
769	3	3	2026-02-18	15
770	3	3	2026-02-19	25
771	3	3	2026-02-20	10
772	3	3	2026-02-21	11
773	3	3	2026-02-22	12
774	3	3	2026-02-23	13
775	3	3	2026-02-24	14
776	3	3	2026-02-25	15
777	3	3	2026-02-26	25
778	3	3	2026-02-27	10
779	3	3	2026-02-28	11
780	3	3	2026-03-01	12
781	3	3	2026-03-02	13
782	3	3	2026-03-03	14
783	3	3	2026-03-04	15
784	3	3	2026-03-05	25
785	3	3	2026-03-06	10
786	3	3	2026-03-07	11
787	3	3	2026-03-08	12
788	3	3	2026-03-09	13
789	3	3	2026-03-10	14
790	3	3	2026-03-11	15
791	3	3	2026-03-12	25
792	3	3	2026-03-13	10
793	3	3	2026-03-14	11
794	3	3	2026-03-15	12
795	3	3	2026-03-16	13
796	3	3	2026-03-17	14
797	3	3	2026-03-18	15
798	3	3	2026-03-19	25
799	3	3	2026-03-20	10
800	3	3	2026-03-21	11
801	3	3	2026-03-22	12
802	3	3	2026-03-23	13
803	3	3	2026-03-24	14
804	3	3	2026-03-25	15
805	3	3	2026-03-26	25
806	3	3	2026-03-27	10
807	3	3	2026-03-28	11
808	3	3	2026-03-29	12
809	3	3	2026-03-30	13
810	3	3	2026-03-31	14
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventory (inventory_id, product_id, warehouse_id, retailer_id, quantity, reorder_point, safety_stock) FROM stdin;
1	1	1	\N	500	150	75
2	1	2	\N	500	150	75
3	1	3	\N	500	150	75
4	1	\N	1	100	40	20
5	1	\N	2	100	40	20
6	1	\N	3	100	40	20
7	2	1	\N	500	150	75
8	2	2	\N	500	150	75
9	2	3	\N	500	150	75
10	2	\N	1	100	40	20
11	2	\N	2	100	40	20
12	2	\N	3	100	40	20
13	3	1	\N	500	150	75
14	3	2	\N	500	150	75
15	3	3	\N	500	150	75
16	3	\N	1	100	40	20
17	3	\N	2	100	40	20
18	3	\N	3	100	40	20
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (order_id, product_id, source_type, source_id, destination_type, destination_id, quantity, order_date, expected_delivery_date, status) FROM stdin;
1	1	supplier	1	warehouse	1	200	2026-04-01	2026-04-08	delivered
2	2	supplier	2	warehouse	2	200	2026-04-02	2026-04-09	delivered
3	3	supplier	3	warehouse	3	200	2026-04-03	2026-04-10	delivered
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (product_id, product_name, category, unit_price, supplier_id) FROM stdin;
1	Laptop	Electronics	150000	1
2	Smartphone	Electronics	65000	2
3	Headphones	Accessories	5000	3
\.


--
-- Data for Name: retailers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.retailers (retailer_id, retailer_name, location) FROM stdin;
1	Lahore Retail Store	Lahore
2	Karachi Retail Store	Karachi
3	Islamabad Retail Store	Islamabad
\.


--
-- Data for Name: shipments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.shipments (shipment_id, order_id, shipped_date, expected_arrival_date, actual_arrival_date, status) FROM stdin;
1	1	2026-04-01	2026-04-08	2026-04-09	delivered
2	2	2026-04-02	2026-04-09	2026-04-10	delivered
3	3	2026-04-03	2026-04-10	2026-04-11	delivered
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.suppliers (supplier_id, supplier_name, location, average_lead_time_days, reliability_score) FROM stdin;
1	Alpha Manufacturing	Lahore	5	0.95
2	Beta Industries	Karachi	8	0.88
3	Gamma Supplies	Islamabad	3	0.97
\.


--
-- Data for Name: warehouses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.warehouses (warehouse_id, warehouse_name, location, capacity) FROM stdin;
1	Lahore Central Warehouse	Lahore	10000
2	Karachi Distribution Center	Karachi	15000
3	Islamabad Regional Warehouse	Islamabad	8000
\.


--
-- Name: demand_history_demand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.demand_history_demand_id_seq', 810, true);


--
-- Name: inventory_inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventory_inventory_id_seq', 18, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 3, true);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_product_id_seq', 3, true);


--
-- Name: retailers_retailer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.retailers_retailer_id_seq', 3, true);


--
-- Name: shipments_shipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.shipments_shipment_id_seq', 3, true);


--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.suppliers_supplier_id_seq', 3, true);


--
-- Name: warehouses_warehouse_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.warehouses_warehouse_id_seq', 3, true);


--
-- Name: demand_history demand_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demand_history
    ADD CONSTRAINT demand_history_pkey PRIMARY KEY (demand_id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (inventory_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: retailers retailers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.retailers
    ADD CONSTRAINT retailers_pkey PRIMARY KEY (retailer_id);


--
-- Name: shipments shipments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_pkey PRIMARY KEY (shipment_id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (warehouse_id);


--
-- Name: demand_history demand_history_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demand_history
    ADD CONSTRAINT demand_history_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: demand_history demand_history_retailer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.demand_history
    ADD CONSTRAINT demand_history_retailer_id_fkey FOREIGN KEY (retailer_id) REFERENCES public.retailers(retailer_id);


--
-- Name: inventory inventory_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: inventory inventory_retailer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_retailer_id_fkey FOREIGN KEY (retailer_id) REFERENCES public.retailers(retailer_id);


--
-- Name: inventory inventory_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(warehouse_id);


--
-- Name: orders orders_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: products products_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id);


--
-- Name: shipments shipments_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipments_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id);


--
-- PostgreSQL database dump complete
--

\unrestrict YHc7ycNiYlEjO7M3fmy9eNhRNKjTnZeAfcbCdv9RQUnhoozS54GERtqeqpOStMH

