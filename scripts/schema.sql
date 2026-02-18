--
-- PostgreSQL database dump
--


-- Dumped from database version 17.7 (bdd1736)
-- Dumped by pg_dump version 18.1

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

--
-- Name: benchmark; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA benchmark;


--
-- Name: neon_auth; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA neon_auth;


--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: image_status; Type: TYPE; Schema: benchmark; Owner: -
--

CREATE TYPE benchmark.image_status AS ENUM (
    'pending_upload',
    'active',
    'upload_failed',
    'deleted'
);


--
-- Name: run_status; Type: TYPE; Schema: benchmark; Owner: -
--

CREATE TYPE benchmark.run_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed',
    'cancelled'
);


--
-- Name: image_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.image_status AS ENUM (
    'pending_upload',
    'active',
    'upload_failed',
    'deleted'
);


--
-- Name: run_status; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.run_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed',
    'cancelled'
);


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: benchmark; Owner: -
--

CREATE FUNCTION benchmark.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: datasets; Type: TABLE; Schema: benchmark; Owner: -
--

CREATE TABLE benchmark.datasets (
    dataset_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    version character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: evaluation_runs; Type: TABLE; Schema: benchmark; Owner: -
--

CREATE TABLE benchmark.evaluation_runs (
    run_id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_name character varying(255) NOT NULL,
    model_version character varying(100),
    dataset_id uuid,
    dataset_version character varying(50),
    config jsonb DEFAULT '{}'::jsonb,
    status benchmark.run_status DEFAULT 'pending'::benchmark.run_status NOT NULL,
    error_message text,
    total_images integer DEFAULT 0,
    processed_images integer DEFAULT 0,
    failed_images integer DEFAULT 0,
    started_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    initiated_by character varying(255)
);


--
-- Name: images; Type: TABLE; Schema: benchmark; Owner: -
--

CREATE TABLE benchmark.images (
    image_id uuid DEFAULT gen_random_uuid() NOT NULL,
    dataset_id uuid,
    file_path character varying(512) NOT NULL,
    s3_etag character varying(64),
    status benchmark.image_status DEFAULT 'pending_upload'::benchmark.image_status NOT NULL,
    width integer,
    height integer,
    format character varying(20),
    file_size_bytes bigint,
    image_type character varying(100),
    metadata jsonb DEFAULT '{}'::jsonb,
    ground_truth jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: metrics; Type: TABLE; Schema: benchmark; Owner: -
--

CREATE TABLE benchmark.metrics (
    metric_id uuid DEFAULT gen_random_uuid() NOT NULL,
    prediction_id uuid NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_value double precision NOT NULL,
    meta_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: predictions; Type: TABLE; Schema: benchmark; Owner: -
--

CREATE TABLE benchmark.predictions (
    prediction_id uuid DEFAULT gen_random_uuid() NOT NULL,
    image_id uuid NOT NULL,
    run_id uuid NOT NULL,
    output jsonb,
    raw_response text,
    latency_ms integer,
    input_tokens integer,
    output_tokens integer,
    success boolean DEFAULT true NOT NULL,
    error_message text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: prediction_details; Type: VIEW; Schema: benchmark; Owner: -
--

CREATE VIEW benchmark.prediction_details AS
 SELECT p.prediction_id,
    i.image_id,
    i.file_path,
    i.image_type,
    er.model_name,
    er.model_version,
    p.success,
    p.latency_ms,
    m.metric_name,
    m.metric_value
   FROM (((benchmark.predictions p
     JOIN benchmark.images i ON ((p.image_id = i.image_id)))
     JOIN benchmark.evaluation_runs er ON ((p.run_id = er.run_id)))
     LEFT JOIN benchmark.metrics m ON ((p.prediction_id = m.prediction_id)));


--
-- Name: run_summary; Type: VIEW; Schema: benchmark; Owner: -
--

CREATE VIEW benchmark.run_summary AS
 SELECT er.run_id,
    er.model_name,
    er.model_version,
    d.name AS dataset_name,
    er.status,
    er.processed_images,
    er.failed_images,
    er.started_at,
    er.completed_at,
    EXTRACT(epoch FROM (er.completed_at - er.started_at)) AS duration_seconds
   FROM (benchmark.evaluation_runs er
     LEFT JOIN benchmark.datasets d ON ((er.dataset_id = d.dataset_id)));


--
-- Name: account; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.account (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "accountId" text NOT NULL,
    "providerId" text NOT NULL,
    "userId" uuid NOT NULL,
    "accessToken" text,
    "refreshToken" text,
    "idToken" text,
    "accessTokenExpiresAt" timestamp with time zone,
    "refreshTokenExpiresAt" timestamp with time zone,
    scope text,
    password text,
    "createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp with time zone NOT NULL
);


--
-- Name: invitation; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.invitation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "organizationId" uuid NOT NULL,
    email text NOT NULL,
    role text,
    status text NOT NULL,
    "expiresAt" timestamp with time zone NOT NULL,
    "createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "inviterId" uuid NOT NULL
);


--
-- Name: jwks; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.jwks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "publicKey" text NOT NULL,
    "privateKey" text NOT NULL,
    "createdAt" timestamp with time zone NOT NULL,
    "expiresAt" timestamp with time zone
);


--
-- Name: member; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.member (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "organizationId" uuid NOT NULL,
    "userId" uuid NOT NULL,
    role text NOT NULL,
    "createdAt" timestamp with time zone NOT NULL
);


--
-- Name: organization; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.organization (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    slug text NOT NULL,
    logo text,
    "createdAt" timestamp with time zone NOT NULL,
    metadata text
);


--
-- Name: project_config; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.project_config (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    endpoint_id text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    trusted_origins jsonb NOT NULL,
    social_providers jsonb NOT NULL,
    email_provider jsonb,
    email_and_password jsonb,
    allow_localhost boolean NOT NULL
);


--
-- Name: session; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.session (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "expiresAt" timestamp with time zone NOT NULL,
    token text NOT NULL,
    "createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp with time zone NOT NULL,
    "ipAddress" text,
    "userAgent" text,
    "userId" uuid NOT NULL,
    "impersonatedBy" text,
    "activeOrganizationId" text
);


--
-- Name: user; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth."user" (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    "emailVerified" boolean NOT NULL,
    image text,
    "createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    role text,
    banned boolean,
    "banReason" text,
    "banExpires" timestamp with time zone
);


--
-- Name: verification; Type: TABLE; Schema: neon_auth; Owner: -
--

CREATE TABLE neon_auth.verification (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    identifier text NOT NULL,
    value text NOT NULL,
    "expiresAt" timestamp with time zone NOT NULL,
    "createdAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: inference_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inference_models (
    id integer NOT NULL,
    model_name text NOT NULL,
    inference_type text,
    inference_class text,
    requires_gpu boolean,
    default_config jsonb,
    version integer NOT NULL,
    multimodal boolean NOT NULL,
    avg_latency double precision,
    top_percentile_accuracy double precision,
    latest_eval_accuracy double precision,
    latest_eval_datetime timestamp with time zone
);


--
-- Name: inference_models_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inference_models_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inference_models_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inference_models_id_seq OWNED BY public.inference_models.id;


--
-- Name: inference_models id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inference_models ALTER COLUMN id SET DEFAULT nextval('public.inference_models_id_seq'::regclass);


--
-- Name: datasets datasets_name_key; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.datasets
    ADD CONSTRAINT datasets_name_key UNIQUE (name);


--
-- Name: datasets datasets_pkey; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (dataset_id);


--
-- Name: evaluation_runs evaluation_runs_pkey; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.evaluation_runs
    ADD CONSTRAINT evaluation_runs_pkey PRIMARY KEY (run_id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (image_id);


--
-- Name: metrics metrics_pkey; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.metrics
    ADD CONSTRAINT metrics_pkey PRIMARY KEY (metric_id);


--
-- Name: metrics metrics_prediction_id_metric_name_key; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.metrics
    ADD CONSTRAINT metrics_prediction_id_metric_name_key UNIQUE (prediction_id, metric_name);


--
-- Name: predictions predictions_image_id_run_id_key; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.predictions
    ADD CONSTRAINT predictions_image_id_run_id_key UNIQUE (image_id, run_id);


--
-- Name: predictions predictions_pkey; Type: CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.predictions
    ADD CONSTRAINT predictions_pkey PRIMARY KEY (prediction_id);


--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- Name: invitation invitation_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.invitation
    ADD CONSTRAINT invitation_pkey PRIMARY KEY (id);


--
-- Name: jwks jwks_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.jwks
    ADD CONSTRAINT jwks_pkey PRIMARY KEY (id);


--
-- Name: member member_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: organization organization_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.organization
    ADD CONSTRAINT organization_pkey PRIMARY KEY (id);


--
-- Name: organization organization_slug_key; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.organization
    ADD CONSTRAINT organization_slug_key UNIQUE (slug);


--
-- Name: project_config project_config_endpoint_id_key; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.project_config
    ADD CONSTRAINT project_config_endpoint_id_key UNIQUE (endpoint_id);


--
-- Name: project_config project_config_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.project_config
    ADD CONSTRAINT project_config_pkey PRIMARY KEY (id);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: session session_token_key; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.session
    ADD CONSTRAINT session_token_key UNIQUE (token);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: verification verification_pkey; Type: CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.verification
    ADD CONSTRAINT verification_pkey PRIMARY KEY (id);


--
-- Name: inference_models inference_models_model_name_version_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inference_models
    ADD CONSTRAINT inference_models_model_name_version_key UNIQUE (model_name, version);


--
-- Name: inference_models inference_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inference_models
    ADD CONSTRAINT inference_models_pkey PRIMARY KEY (id);


--
-- Name: idx_images_dataset; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_images_dataset ON benchmark.images USING btree (dataset_id);


--
-- Name: idx_images_status; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_images_status ON benchmark.images USING btree (status);


--
-- Name: idx_images_type; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_images_type ON benchmark.images USING btree (image_type);


--
-- Name: idx_metrics_name; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_metrics_name ON benchmark.metrics USING btree (metric_name);


--
-- Name: idx_metrics_prediction; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_metrics_prediction ON benchmark.metrics USING btree (prediction_id);


--
-- Name: idx_metrics_value; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_metrics_value ON benchmark.metrics USING btree (metric_value);


--
-- Name: idx_predictions_image; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_predictions_image ON benchmark.predictions USING btree (image_id);


--
-- Name: idx_predictions_run; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_predictions_run ON benchmark.predictions USING btree (run_id);


--
-- Name: idx_predictions_success; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_predictions_success ON benchmark.predictions USING btree (success);


--
-- Name: idx_runs_dataset; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_runs_dataset ON benchmark.evaluation_runs USING btree (dataset_id);


--
-- Name: idx_runs_model; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_runs_model ON benchmark.evaluation_runs USING btree (model_name, model_version);


--
-- Name: idx_runs_status; Type: INDEX; Schema: benchmark; Owner: -
--

CREATE INDEX idx_runs_status ON benchmark.evaluation_runs USING btree (status);


--
-- Name: account_userId_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX "account_userId_idx" ON neon_auth.account USING btree ("userId");


--
-- Name: invitation_email_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX invitation_email_idx ON neon_auth.invitation USING btree (email);


--
-- Name: invitation_organizationId_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX "invitation_organizationId_idx" ON neon_auth.invitation USING btree ("organizationId");


--
-- Name: member_organizationId_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX "member_organizationId_idx" ON neon_auth.member USING btree ("organizationId");


--
-- Name: member_userId_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX "member_userId_idx" ON neon_auth.member USING btree ("userId");


--
-- Name: session_userId_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX "session_userId_idx" ON neon_auth.session USING btree ("userId");


--
-- Name: verification_identifier_idx; Type: INDEX; Schema: neon_auth; Owner: -
--

CREATE INDEX verification_identifier_idx ON neon_auth.verification USING btree (identifier);


--
-- Name: datasets update_datasets_updated_at; Type: TRIGGER; Schema: benchmark; Owner: -
--

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON benchmark.datasets FOR EACH ROW EXECUTE FUNCTION benchmark.update_updated_at_column();


--
-- Name: images update_images_updated_at; Type: TRIGGER; Schema: benchmark; Owner: -
--

CREATE TRIGGER update_images_updated_at BEFORE UPDATE ON benchmark.images FOR EACH ROW EXECUTE FUNCTION benchmark.update_updated_at_column();


--
-- Name: evaluation_runs evaluation_runs_dataset_id_fkey; Type: FK CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.evaluation_runs
    ADD CONSTRAINT evaluation_runs_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES benchmark.datasets(dataset_id) ON DELETE SET NULL;


--
-- Name: images images_dataset_id_fkey; Type: FK CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.images
    ADD CONSTRAINT images_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES benchmark.datasets(dataset_id) ON DELETE SET NULL;


--
-- Name: metrics metrics_prediction_id_fkey; Type: FK CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.metrics
    ADD CONSTRAINT metrics_prediction_id_fkey FOREIGN KEY (prediction_id) REFERENCES benchmark.predictions(prediction_id) ON DELETE CASCADE;


--
-- Name: predictions predictions_image_id_fkey; Type: FK CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.predictions
    ADD CONSTRAINT predictions_image_id_fkey FOREIGN KEY (image_id) REFERENCES benchmark.images(image_id) ON DELETE CASCADE;


--
-- Name: predictions predictions_run_id_fkey; Type: FK CONSTRAINT; Schema: benchmark; Owner: -
--

ALTER TABLE ONLY benchmark.predictions
    ADD CONSTRAINT predictions_run_id_fkey FOREIGN KEY (run_id) REFERENCES benchmark.evaluation_runs(run_id) ON DELETE CASCADE;


--
-- Name: account account_userId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.account
    ADD CONSTRAINT "account_userId_fkey" FOREIGN KEY ("userId") REFERENCES neon_auth."user"(id) ON DELETE CASCADE;


--
-- Name: invitation invitation_inviterId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.invitation
    ADD CONSTRAINT "invitation_inviterId_fkey" FOREIGN KEY ("inviterId") REFERENCES neon_auth."user"(id) ON DELETE CASCADE;


--
-- Name: invitation invitation_organizationId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.invitation
    ADD CONSTRAINT "invitation_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES neon_auth.organization(id) ON DELETE CASCADE;


--
-- Name: member member_organizationId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.member
    ADD CONSTRAINT "member_organizationId_fkey" FOREIGN KEY ("organizationId") REFERENCES neon_auth.organization(id) ON DELETE CASCADE;


--
-- Name: member member_userId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.member
    ADD CONSTRAINT "member_userId_fkey" FOREIGN KEY ("userId") REFERENCES neon_auth."user"(id) ON DELETE CASCADE;


--
-- Name: session session_userId_fkey; Type: FK CONSTRAINT; Schema: neon_auth; Owner: -
--

ALTER TABLE ONLY neon_auth.session
    ADD CONSTRAINT "session_userId_fkey" FOREIGN KEY ("userId") REFERENCES neon_auth."user"(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


