--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: merge_quota(); Type: FUNCTION; Schema: public; Owner: postfix
--

CREATE FUNCTION merge_quota() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            UPDATE quota SET current = NEW.current + current WHERE username = NEW.username AND path = NEW.path;
            IF found THEN
                RETURN NULL;
            ELSE
                RETURN NEW;
            END IF;
      END;
      $$;


ALTER FUNCTION public.merge_quota() OWNER TO postfix;

--
-- Name: merge_quota2(); Type: FUNCTION; Schema: public; Owner: postfix
--

CREATE FUNCTION merge_quota2() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
        BEGIN
            IF NEW.messages < 0 OR NEW.messages IS NULL THEN
                -- ugly kludge: we came here from this function, really do try to insert
                IF NEW.messages IS NULL THEN
                    NEW.messages = 0;
                ELSE
                    NEW.messages = -NEW.messages;
                END IF;
                return NEW;
            END IF;

            LOOP
                UPDATE quota2 SET bytes = bytes + NEW.bytes,
                    messages = messages + NEW.messages
                    WHERE username = NEW.username;
                IF found THEN
                    RETURN NULL;
                END IF;

                BEGIN
                    IF NEW.messages = 0 THEN
                    INSERT INTO quota2 (bytes, messages, username) VALUES (NEW.bytes, NULL, NEW.username);
                    ELSE
                        INSERT INTO quota2 (bytes, messages, username) VALUES (NEW.bytes, -NEW.messages, NEW.username);
                    END IF;
                    return NULL;
                    EXCEPTION WHEN unique_violation THEN
                    -- someone just inserted the record, update it
                END;
            END LOOP;
        END;
        $$;


ALTER FUNCTION public.merge_quota2() OWNER TO postfix;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: admin; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE admin (
    username character varying(255) NOT NULL,
    password character varying(255) DEFAULT ''::character varying NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL,
    superadmin boolean DEFAULT false NOT NULL
);


ALTER TABLE admin OWNER TO postfix;

--
-- Name: TABLE admin; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE admin IS 'Postfix Admin - Virtual Admins';


--
-- Name: alias; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE alias (
    address character varying(255) NOT NULL,
    goto text NOT NULL,
    domain character varying(255) NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL,
    comment character varying(255)
);


ALTER TABLE alias OWNER TO postfix;

--
-- Name: TABLE alias; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE alias IS 'Postfix Admin - Virtual Aliases';


--
-- Name: COLUMN alias.comment; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON COLUMN alias.comment IS 'ajout perso';


--
-- Name: alias_domain; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE alias_domain (
    alias_domain character varying(255) NOT NULL,
    target_domain character varying(255) NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL
);


ALTER TABLE alias_domain OWNER TO postfix;

--
-- Name: TABLE alias_domain; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE alias_domain IS 'Postfix Admin - Domain Aliases';


--
-- Name: config; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE config (
    id integer NOT NULL,
    name character varying(20) NOT NULL,
    value character varying(20) NOT NULL
);


ALTER TABLE config OWNER TO postfix;

--
-- Name: config_id_seq; Type: SEQUENCE; Schema: public; Owner: postfix
--

CREATE SEQUENCE config_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE config_id_seq OWNER TO postfix;

--
-- Name: config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postfix
--

ALTER SEQUENCE config_id_seq OWNED BY config.id;


--
-- Name: domain; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE domain (
    domain character varying(255) NOT NULL,
    description character varying(255) DEFAULT ''::character varying NOT NULL,
    aliases integer DEFAULT 0 NOT NULL,
    mailboxes integer DEFAULT 0 NOT NULL,
    maxquota bigint DEFAULT 0 NOT NULL,
    quota bigint DEFAULT 0 NOT NULL,
    transport character varying(255) DEFAULT NULL::character varying,
    backupmx boolean DEFAULT false NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL
);


ALTER TABLE domain OWNER TO postfix;

--
-- Name: TABLE domain; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE domain IS 'Postfix Admin - Virtual Domains';


--
-- Name: domain_admins; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE domain_admins (
    username character varying(255) NOT NULL,
    domain character varying(255) NOT NULL,
    created timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL
);


ALTER TABLE domain_admins OWNER TO postfix;

--
-- Name: TABLE domain_admins; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE domain_admins IS 'Postfix Admin - Domain Admins';


--
-- Name: fetchmail; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE fetchmail (
    id integer NOT NULL,
    mailbox character varying(255) DEFAULT ''::character varying NOT NULL,
    src_server character varying(255) DEFAULT ''::character varying NOT NULL,
    src_auth character varying(15) NOT NULL,
    src_user character varying(255) DEFAULT ''::character varying NOT NULL,
    src_password character varying(255) DEFAULT ''::character varying NOT NULL,
    src_folder character varying(255) DEFAULT ''::character varying NOT NULL,
    poll_time integer DEFAULT 10 NOT NULL,
    fetchall boolean DEFAULT false NOT NULL,
    keep boolean DEFAULT false NOT NULL,
    protocol character varying(15) NOT NULL,
    extra_options text,
    returned_text text,
    mda character varying(255) DEFAULT ''::character varying NOT NULL,
    date timestamp with time zone DEFAULT now(),
    usessl boolean DEFAULT false NOT NULL,
    sslcertck boolean DEFAULT false NOT NULL,
    sslcertpath character varying(255) DEFAULT ''::character varying,
    sslfingerprint character varying(255) DEFAULT ''::character varying,
    domain character varying(255) DEFAULT ''::character varying,
    active boolean DEFAULT false NOT NULL,
    created timestamp with time zone DEFAULT '2000-01-01 00:00:00+01'::timestamp with time zone,
    modified timestamp with time zone DEFAULT now(),
    CONSTRAINT fetchmail_protocol_check CHECK (((protocol)::text = ANY (ARRAY[('POP3'::character varying)::text, ('IMAP'::character varying)::text, ('POP2'::character varying)::text, ('ETRN'::character varying)::text, ('AUTO'::character varying)::text]))),
    CONSTRAINT fetchmail_src_auth_check CHECK (((src_auth)::text = ANY (ARRAY[('password'::character varying)::text, ('kerberos_v5'::character varying)::text, ('kerberos'::character varying)::text, ('kerberos_v4'::character varying)::text, ('gssapi'::character varying)::text, ('cram-md5'::character varying)::text, ('otp'::character varying)::text, ('ntlm'::character varying)::text, ('msn'::character varying)::text, ('ssh'::character varying)::text, ('any'::character varying)::text])))
);


ALTER TABLE fetchmail OWNER TO postfix;

--
-- Name: fetchmail_id_seq; Type: SEQUENCE; Schema: public; Owner: postfix
--

CREATE SEQUENCE fetchmail_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE fetchmail_id_seq OWNER TO postfix;

--
-- Name: fetchmail_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postfix
--

ALTER SEQUENCE fetchmail_id_seq OWNED BY fetchmail.id;


--
-- Name: log; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE log (
    "timestamp" timestamp with time zone DEFAULT now(),
    username character varying(255) DEFAULT ''::character varying NOT NULL,
    domain character varying(255) DEFAULT ''::character varying NOT NULL,
    action character varying(255) DEFAULT ''::character varying NOT NULL,
    data text DEFAULT ''::text NOT NULL
);


ALTER TABLE log OWNER TO postfix;

--
-- Name: TABLE log; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE log IS 'Postfix Admin - Log';


--
-- Name: mailbox; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE mailbox (
    username character varying(255) NOT NULL,
    password character varying(255) DEFAULT ''::character varying NOT NULL,
    name character varying(255) DEFAULT ''::character varying NOT NULL,
    maildir character varying(255) DEFAULT ''::character varying NOT NULL,
    quota bigint DEFAULT 0 NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL,
    domain character varying(255),
    local_part character varying(255) NOT NULL
);


ALTER TABLE mailbox OWNER TO postfix;

--
-- Name: TABLE mailbox; Type: COMMENT; Schema: public; Owner: postfix
--

COMMENT ON TABLE mailbox IS 'Postfix Admin - Virtual Mailboxes';


--
-- Name: quota; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE quota (
    username character varying(255) NOT NULL,
    path character varying(100) NOT NULL,
    current bigint
);


ALTER TABLE quota OWNER TO postfix;

--
-- Name: quota2; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE quota2 (
    username character varying(100) NOT NULL,
    bytes bigint DEFAULT 0 NOT NULL,
    messages integer DEFAULT 0 NOT NULL
);


ALTER TABLE quota2 OWNER TO postfix;

--
-- Name: vacation; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE vacation (
    email character varying(255) NOT NULL,
    subject character varying(255) NOT NULL,
    body text DEFAULT ''::text NOT NULL,
    created timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true NOT NULL,
    domain character varying(255),
    modified timestamp with time zone DEFAULT now(),
    activefrom timestamp with time zone DEFAULT '2000-01-01 00:00:00+01'::timestamp with time zone,
    activeuntil timestamp with time zone DEFAULT '2000-01-01 00:00:00+01'::timestamp with time zone,
    interval_time integer DEFAULT 0 NOT NULL
);


ALTER TABLE vacation OWNER TO postfix;

--
-- Name: vacation_notification; Type: TABLE; Schema: public; Owner: postfix
--

CREATE TABLE vacation_notification (
    on_vacation character varying(255) NOT NULL,
    notified character varying(255) NOT NULL,
    notified_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE vacation_notification OWNER TO postfix;

--
-- Name: config id; Type: DEFAULT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY config ALTER COLUMN id SET DEFAULT nextval('config_id_seq'::regclass);


--
-- Name: fetchmail id; Type: DEFAULT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY fetchmail ALTER COLUMN id SET DEFAULT nextval('fetchmail_id_seq'::regclass);


--
-- Name: admin admin_key; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY admin
    ADD CONSTRAINT admin_key PRIMARY KEY (username);


--
-- Name: alias_domain alias_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY alias_domain
    ADD CONSTRAINT alias_domain_pkey PRIMARY KEY (alias_domain);


--
-- Name: alias alias_key; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY alias
    ADD CONSTRAINT alias_key PRIMARY KEY (address);


--
-- Name: config config_name_key; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY config
    ADD CONSTRAINT config_name_key UNIQUE (name);


--
-- Name: config config_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY config
    ADD CONSTRAINT config_pkey PRIMARY KEY (id);


--
-- Name: domain domain_key; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY domain
    ADD CONSTRAINT domain_key PRIMARY KEY (domain);


--
-- Name: fetchmail fetchmail_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY fetchmail
    ADD CONSTRAINT fetchmail_pkey PRIMARY KEY (id);


--
-- Name: mailbox mailbox_key; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY mailbox
    ADD CONSTRAINT mailbox_key PRIMARY KEY (username);


--
-- Name: quota2 quota2_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY quota2
    ADD CONSTRAINT quota2_pkey PRIMARY KEY (username);


--
-- Name: quota quota_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY quota
    ADD CONSTRAINT quota_pkey PRIMARY KEY (username, path);


--
-- Name: vacation_notification vacation_notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY vacation_notification
    ADD CONSTRAINT vacation_notification_pkey PRIMARY KEY (on_vacation, notified);


--
-- Name: vacation vacation_pkey; Type: CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY vacation
    ADD CONSTRAINT vacation_pkey PRIMARY KEY (email);


--
-- Name: alias_address_active; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX alias_address_active ON alias USING btree (address, active);


--
-- Name: alias_domain_active; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX alias_domain_active ON alias_domain USING btree (alias_domain, active);


--
-- Name: alias_domain_idx; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX alias_domain_idx ON alias USING btree (domain);


--
-- Name: domain_domain_active; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX domain_domain_active ON domain USING btree (domain, active);


--
-- Name: log_domain_timestamp_idx; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX log_domain_timestamp_idx ON log USING btree (domain, "timestamp");


--
-- Name: mailbox_domain_idx; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX mailbox_domain_idx ON mailbox USING btree (domain);


--
-- Name: mailbox_username_active; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX mailbox_username_active ON mailbox USING btree (username, active);


--
-- Name: vacation_email_active; Type: INDEX; Schema: public; Owner: postfix
--

CREATE INDEX vacation_email_active ON vacation USING btree (email, active);


--
-- Name: quota mergequota; Type: TRIGGER; Schema: public; Owner: postfix
--

CREATE TRIGGER mergequota BEFORE INSERT ON quota FOR EACH ROW EXECUTE PROCEDURE merge_quota();


--
-- Name: quota2 mergequota2; Type: TRIGGER; Schema: public; Owner: postfix
--

CREATE TRIGGER mergequota2 BEFORE INSERT ON quota2 FOR EACH ROW EXECUTE PROCEDURE merge_quota2();


--
-- Name: alias_domain alias_domain_alias_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY alias_domain
    ADD CONSTRAINT alias_domain_alias_domain_fkey FOREIGN KEY (alias_domain) REFERENCES domain(domain) ON DELETE CASCADE;


--
-- Name: alias alias_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY alias
    ADD CONSTRAINT alias_domain_fkey FOREIGN KEY (domain) REFERENCES domain(domain);


--
-- Name: alias_domain alias_domain_target_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY alias_domain
    ADD CONSTRAINT alias_domain_target_domain_fkey FOREIGN KEY (target_domain) REFERENCES domain(domain) ON DELETE CASCADE;


--
-- Name: domain_admins domain_admins_domain_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY domain_admins
    ADD CONSTRAINT domain_admins_domain_fkey FOREIGN KEY (domain) REFERENCES domain(domain);


--
-- Name: mailbox mailbox_domain_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY mailbox
    ADD CONSTRAINT mailbox_domain_fkey1 FOREIGN KEY (domain) REFERENCES domain(domain);


--
-- Name: vacation vacation_domain_fkey1; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY vacation
    ADD CONSTRAINT vacation_domain_fkey1 FOREIGN KEY (domain) REFERENCES domain(domain);


--
-- Name: vacation_notification vacation_notification_on_vacation_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postfix
--

ALTER TABLE ONLY vacation_notification
    ADD CONSTRAINT vacation_notification_on_vacation_fkey FOREIGN KEY (on_vacation) REFERENCES vacation(email) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

