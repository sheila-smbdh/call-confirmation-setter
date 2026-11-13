-- Call Confirmation Tracker (Gino): history store in the setter-data project (ref suoblmuvrmyfmuvlhqce).
-- Run once in the Supabase SQL editor. Creates tables only; touches nothing that already exists.
-- All tables are in `public` (the only schema the REST API exposes) and start with `call_confirm_`.
-- RLS is on with no policies: the anon key can't read or write them; the project's service key can.

-- One row per nightly run.
create table if not exists public.call_confirm_runs (
  run_id        text primary key,            -- e.g. 2026-11-13T20:00-07:00
  today         date not null,               -- run date (US Eastern)
  data_through  date,                        -- last day the tracker judged
  status        text,                        -- ok / failed / partial
  summary       jsonb,                       -- counts, warnings
  created_at    timestamptz not null default now()
);

-- Where each incremental scan left off (e.g. the last Slack ts read in #cc-gino).
create table if not exists public.call_confirm_sync_state (
  source        text primary key,            -- slack_cc_gino, slack_call_confirmation, slack_closer_eod, close_activity, calendly
  last_ts       text,                        -- Slack ts, or ISO time, of the newest item read
  full_scans    int  not null default 0,     -- how many full-history scans have run
  last_run_id   text,
  note          text,
  updated_at    timestamptz not null default now()
);

-- Everything pulled from a source, kept as the source returned it.
-- source: close_call, close_sms, close_event, close_meeting, close_status_change, close_calendar_response,
--         close_call_transcript, calendly_event, calendly_invitee, slack_call_confirmation, slack_closer_eod,
--         slack_cc_gino, judgment_override, lead_fix
create table if not exists public.call_confirm_raw_records (
  source        text not null,
  record_id     text not null,
  lead_id       text,
  occurred_at   timestamptz,
  payload       jsonb not null,
  last_run_id   text,
  first_seen_at timestamptz not null default now(),
  last_seen_at  timestamptz not null default now(),
  primary key (source, record_id)
);
create index if not exists call_confirm_raw_records_lead on public.call_confirm_raw_records (lead_id);
create index if not exists call_confirm_raw_records_time on public.call_confirm_raw_records (source, occurred_at);

-- The Calls tab: one row per booked call (Calendly event), current state.
create table if not exists public.call_confirm_calls (
  event_uri     text primary key,
  lead_id       text,
  lead_name     text,
  email         text,
  closer        text,
  call_date     date,
  call_et       text,
  booked_date   date,
  booked_et     text,
  booking_type  text,                        -- During shift / Overnight
  logging_check text,
  happened      text,
  row           jsonb not null,              -- the full tracker row (every column)
  last_run_id   text,
  updated_at    timestamptz not null default now()
);
create index if not exists call_confirm_calls_lead on public.call_confirm_calls (lead_id);
create index if not exists call_confirm_calls_date on public.call_confirm_calls (call_date);

-- Daily, Weekly and Management tabs as the sheet computed them (values, not formulas).
create table if not exists public.call_confirm_daily (
  day           date primary key,
  row           jsonb not null,
  last_run_id   text,
  updated_at    timestamptz not null default now()
);
create table if not exists public.call_confirm_weekly (
  week_start    date primary key,
  row           jsonb not null,
  last_run_id   text,
  updated_at    timestamptz not null default now()
);
create table if not exists public.call_confirm_management_weeks (
  week_start    date primary key,
  row           jsonb not null,              -- approvals, KPIs, bonus, as shown on Management
  last_run_id   text,
  updated_at    timestamptz not null default now()
);

-- Reviews tab, including Sheila's and Jay's decisions.
create table if not exists public.call_confirm_reviews (
  review_key    text primary key,            -- <event>|welcome / daybefore / 545 / logging
  sheet_row     int,
  week_start    date,
  day           date,
  checkpoint    text,
  kind          text,                        -- Miss / Logging error
  lead_name     text,
  what_happened text,
  note          text,
  decision      text,                        -- Counts as a miss / Excused / blank
  reason        text,
  decided_by    text,
  decided_via   text,                        -- sheet / slack
  slack_ts      text,                        -- the approving Slack message, when decided via Slack
  last_run_id   text,
  updated_at    timestamptz not null default now()
);

-- Exceptions Gino raised in #cc-gino and what Sheila or Jay said.
create table if not exists public.call_confirm_slack_approvals (
  raised_ts         text primary key,
  thread_ts         text,
  raised_by         text,
  raised_at         timestamptz,
  lead_ids          text[],
  lead_names        text[],
  call_date_mentioned text,
  asked             text,
  decision          text,                    -- approved / denied / unclear / no response
  decided_by        text,
  decision_ts       text,
  scope             text,                    -- this lead only / general rule going forward
  decision_summary  text,
  last_run_id       text,
  updated_at        timestamptz not null default now()
);

-- A full copy of each tab's values after every run (history of what the sheet showed).
create table if not exists public.call_confirm_tab_snapshots (
  run_id        text not null,
  tab           text not null,
  rows          jsonb not null,
  created_at    timestamptz not null default now(),
  primary key (run_id, tab)
);

do $$
declare t text;
begin
  foreach t in array array['call_confirm_runs','call_confirm_sync_state','call_confirm_raw_records','call_confirm_calls','call_confirm_daily','call_confirm_weekly',
                           'call_confirm_management_weeks','call_confirm_reviews','call_confirm_slack_approvals','call_confirm_tab_snapshots'] loop
    execute format('alter table public.%I enable row level security', t);
  end loop;
end $$;
