-- My Food Tracker v8 -> v9 migration
-- Use this if your Supabase project ALREADY has the v8 tables and data.
-- This keeps existing food/weight/custom-food data and changes the profile key
-- from Supabase Auth user_id to the email address stored in auth.users.
--
-- v9 has NO password authentication. The email is only a profile name/key.
-- WARNING: anyone who enters another person's email can access that profile.

begin;

-- Stop v8 Row Level Security policies because v9 does not use Supabase Auth.
alter table public.food_logs disable row level security;
alter table public.weight_logs disable row level security;
alter table public.custom_foods disable row level security;

drop policy if exists "users manage their food logs" on public.food_logs;
drop policy if exists "users manage their weight logs" on public.weight_logs;
drop policy if exists "users manage their custom foods" on public.custom_foods;

-- Add the new profile key.
alter table public.food_logs add column if not exists user_email text;
alter table public.weight_logs add column if not exists user_email text;
alter table public.custom_foods add column if not exists user_email text;

-- Preserve existing v8 data by looking up the email belonging to each auth user.
update public.food_logs f
set user_email = lower(u.email)
from auth.users u
where f.user_id = u.id
  and f.user_email is null;

update public.weight_logs w
set user_email = lower(u.email)
from auth.users u
where w.user_id = u.id
  and w.user_email is null;

update public.custom_foods c
set user_email = lower(u.email)
from auth.users u
where c.user_id = u.id
  and c.user_email is null;

-- Refuse to continue if an old row could not be mapped to an email.
do $$
begin
  if exists (select 1 from public.food_logs where user_email is null)
     or exists (select 1 from public.weight_logs where user_email is null)
     or exists (select 1 from public.custom_foods where user_email is null) then
    raise exception 'Migration stopped: one or more rows could not be mapped to an email address from auth.users.';
  end if;
end $$;

alter table public.food_logs alter column user_email set not null;
alter table public.weight_logs alter column user_email set not null;
alter table public.custom_foods alter column user_email set not null;

-- Remove the old Auth UUID key. The old FK/unique constraints depend on it.
alter table public.food_logs drop column user_id;
alter table public.weight_logs drop column user_id;
alter table public.custom_foods drop column user_id;

-- v9 uniqueness rules.
create unique index if not exists weight_logs_user_email_date_key
  on public.weight_logs(user_email, weight_date);

create unique index if not exists custom_foods_user_email_name_key
  on public.custom_foods(user_email, name);

-- The Streamlit app uses the public anon key, so allow the anon role to use
-- these tables. There is intentionally no RLS because there is no real login.
grant select, insert, update, delete on public.food_logs to anon, authenticated;
grant select, insert, update, delete on public.weight_logs to anon, authenticated;
grant select, insert, update, delete on public.custom_foods to anon, authenticated;
grant usage, select on all sequences in schema public to anon, authenticated;

commit;
