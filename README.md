# .CSV2YOUTUBEconverter
It uses CSV files from exportify for Spotify playlist info which which is then used to match youtube links accruately without using yt-dlp.
- PROGRAM WILL ASK FOR USERNAME AT FIRST LAUNCH AND IT CAN BE ANYTHING THERE ARE NO RESTRICTIONS.

## Contact

Feel free to reach out to me on social media:
- Instagram: [@the_brama]([https://instagram.com/your_instagram_id](https://www.instagram.com/the_brama?igsh=MWNnaXhseWJ4cG9ydQ==))
  
---
Purpose of the Program
This is a CSV → YouTube link converter with a GUI.
It:
1. Takes a CSV file (e.g., exported from Spotify with song & artist columns).
2. Searches YouTube for matching videos.
3. Uses a Supabase database to cache previously found links (avoid re-searching).
4. Writes results back to a CSV (adds a YouTube Link column).
5. Has controls to pause, stop, and limit requests to avoid hitting YouTube too often.

---
Main Components & Their Roles
1. Libraries & External Services
tkinter → GUI creation (buttons, input boxes, progress bar).
pandas → Reads/writes CSV files easily.
requests → Fetches YouTube search result pages.
urllib.parse → Encodes search queries into URL-safe form.
re → Extracts YouTube video IDs from HTML.
os → File path & existence checks.
time & threading → Adds delays and runs tasks in background threads (so GUI stays responsive).
json → Stores username locally.
random → Adds random cooldown delays after a certain number of YouTube requests.
dotenv → Loads SUPABASE_URL and SUPABASE_KEY from .env.
supabase-py → Connects to Supabase to read/write cached results.
datetime → Timestamps when a link was fetched.

---
2. Username Handling (Local Storage)
CONFIG_FILE → "user_config.json", stores the username so you don’t have to re-enter it.
load_username() → Reads username from JSON if available.
save_username(username) → Saves username to JSON.
get_or_request_username(root) → If username is missing, asks user via popup before continuing.
Purpose: Every YouTube link inserted into Supabase is tagged with the username.

---
3. YouTube Search Logic
get_first_youtube_result(song, artist)
Builds search query: "Song Artist".
Fetches YouTube’s search page HTML.
Uses regex to find the first "videoId".
Returns a full YouTube link.
check_supabase(song, artist)
Looks in Supabase for a cached link for this song+artist.
If found, returns it (saves YouTube request time).
Insert_to_supabase(song, artist, link, username)
Saves a new record to Supabase with timestamp & username.

---
4. CSV Processing
process_csv(file_path, delay_seconds, max_links, username)
Reads CSV into a DataFrame.
Ensures YouTube Link column exists.
Iterates over each row:
1. Skips if already has a link.
2. Skips if song/artist is missing.
3. Checks Supabase for a cached link.
4. If not cached → searches YouTube & saves to Supabase.
5. Inserts link into DataFrame.
6. Updates progress bar & label.
7. Pauses between requests (delay_seconds).
8. Every fetch_limit YouTube requests → random cooldown of 30–120 seconds.
Saves updated CSV with _with_links suffix.

---
5. Request Control & Safety
fetch_limit (default 20) → After X YouTube requests, script waits randomly to avoid being blocked.
update_fetch_limit() → Lets user change fetch limit in GUI.
is_paused → If True, processing loop stops temporarily until resumed.
stop_requested → If True, processing loop ends early.

---
6. GUI Controls
Elements:
File selection (entry_file, Browse button).
Delay between searches (entry_delay).
Max links to fetch (entry_limit).
Progress bar + label.
Start (btn_start), Pause/Resume (btn_pause), Stop & Save (btn_stop).
Fetch limit updater (entry_fetch_limit, Update button).

Functions:
browse_file() → Opens file dialog for CSV selection.
start_processing() → Starts background thread with process_csv.
toggle_pause() → Switches between Pause/Resume.
stop_and_save() → Stops loop after current iteration.

---
7. Supabase Database Table Expected Fields
Table: "fetched_links"
song → Track name.
artist → Artist name(s).
youtube_link → Fetched YouTube URL.
username → From local config.
fetched_at → UTC timestamp.

---
Flow of Program Execution
1. Startup
Loads .env for Supabase credentials.
Gets username from local config or asks user.
Builds GUI.
2. User Input
Selects CSV.
Sets delay & limits.
Presses Start.
3. Processing
Runs process_csv() in background thread.
For each song:
Checks Supabase for cached link.
If missing, searches YouTube.
Inserts into Supabase.
Updates progress bar.
4. Safety
Random sleep after certain number of YouTube requests.
User can Pause, Resume, or Stop.
5. Finish
Saves updated CSV with links.
Shows completion popup.

---
Key Behavior Control Points
Delay between searches → entry_delay value.
Max number of links → entry_limit value.
Pause/Resume → is_paused flag.
Stop Early → stop_requested flag.
YouTube search frequency control → fetch_limit & random cooldown.
Supabase Caching → check_supabase() before get_first_youtube_result().

---

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
