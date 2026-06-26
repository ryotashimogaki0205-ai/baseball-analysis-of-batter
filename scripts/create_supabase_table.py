from supabase import create_client
import os

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://hpzpkdyvjlvpfzbeddax.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY', None) or os.getenv('SUPABASE_KEY')

if not SUPABASE_KEY:
    print('No service key available in environment. Set SUPABASE_SERVICE_KEY.')
    raise SystemExit(1)

client = create_client(SUPABASE_URL, SUPABASE_KEY)

sql = '''
CREATE TABLE IF NOT EXISTS public.batting_data (
  id serial PRIMARY KEY,
  team_name text,
  player_name text,
  plate_id text,
  course text,
  pitch_type text,
  catch_position text,
  batted_ball_angle double precision,
  pitcher_hand text,
  count text,
  result text,
  input_datetime timestamp with time zone
);
'''

print('Attempting to run SQL via RPC run_sql...')
try:
    res = client.rpc('run_sql', {'sql': sql})
    print('RPC run_sql response:', res)
except Exception as e:
    print('RPC run_sql failed:', e)

# Fallback: try direct POST to /rest/v1/rpc/run_sql using requests
import requests
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}
url = SUPABASE_URL.rstrip('/') + '/rest/v1/rpc/run_sql'
print('Attempting HTTP POST to', url)
try:
    r = requests.post(url, headers=headers, json={'sql': sql})
    print('HTTP status:', r.status_code)
    try:
        print('HTTP response:', r.json())
    except Exception:
        print('HTTP text response:', r.text)
except Exception as e:
    print('HTTP POST failed:', e)

print('Done')
