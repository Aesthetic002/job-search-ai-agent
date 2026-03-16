-- Users
CREATE TABLE users (
  id          SERIAL PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  password    TEXT NOT NULL,
  created_at  TIMESTAMP DEFAULT NOW()
);

-- Jobs
CREATE TABLE jobs (
  id           SERIAL PRIMARY KEY,
  title        TEXT NOT NULL,
  company      TEXT,
  location     TEXT,
  description  TEXT,
  source       TEXT,
  posted_at    TIMESTAMP,
  created_at   TIMESTAMP DEFAULT NOW()
);

-- Applications
CREATE TABLE applications (
  id          SERIAL PRIMARY KEY,
  user_id     INT REFERENCES users(id),
  job_id      INT REFERENCES jobs(id),
  status      TEXT DEFAULT 'applied',
  applied_at  TIMESTAMP DEFAULT NOW()
);

-- Resumes
CREATE TABLE resumes (
  id          SERIAL PRIMARY KEY,
  user_id     INT REFERENCES users(id),
  file_url    TEXT,
  parsed_data JSONB,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

-- Interviews
CREATE TABLE interviews (
  id              SERIAL PRIMARY KEY,
  application_id  INT REFERENCES applications(id),
  scheduled_at    TIMESTAMP,
  notes           TEXT,
  created_at      TIMESTAMP DEFAULT NOW()
);
