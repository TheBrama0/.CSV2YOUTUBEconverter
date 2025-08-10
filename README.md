# .CSV2YOUTUBEconverter

-Note:PROGRAM WILL ASK FOR USERNAME WHEN IT IS RUN FOR THE FIRST TIME AND IT CAN BE ANYTHING THERE ARE NO RESTRICTIONS.

Contact
Feel free to reach out to me on social media:
-Instagram: [@the_brama]
  
---
Purpose of the Program
→This is a CSV to YouTube link converter which gives you exect version of songs from Spotify on YouTube with high accuracy.

It:
1. Takes a CSV file (e.g.,exported from "exportify".
2. Searches YouTube for matching videos.
3. Uses a Supabase to cache previously found links (to avoid re-searching).
4. Writes results back to a CSV (adds a YouTube Link column).
5. Has controls to pause, stop, and limit requests to avoid hitting YouTube too often.

---
CSV Processing
Reads CSV,Ensures YouTube Link column exists.
Iteractes over each row:
1. Skips if already has a link.
2. Skips if song/artist is missing.
3. Checks Supabase for a cached link.
4. If not cached → searches YouTube & saves to Supabase.
5. Inserts link into DataFrame.
6. Updates progress bar & label.
7. Pauses between requests.
8. Every fetch_limit YouTube requests → random cooldown of 30–120 seconds.
9. Saves updated CSV with _with_links suffix.

---
Request Control & Safety
→ After "X" YouTube requests,script waits randomly to avoid being blocked.
→ Lets user change fetch limit in GUI.
→ If True, processing loop stops temporarily until resumed.
→ If True, processing loop ends early.

---
GUI Controls
Elements:
File selection.
Delay between searches.
Max links to fetch.
Progress bar + label.
Start, Pause/Resume, Stop & Save.
Fetch limit updater.

---

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
