# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Pham Tran Thanh Lam
- **Student ID**: 2A202600270
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)
Provide API key
Vibe coding and fix errors for generating v2 tools 

---

## II. Debugging Case Study (10 Points)

**Quota Exceed** I create new gemini API key, use the gemini-flash-2.5-lite model to prevent quota exceed, although it's less "smarter"
**Local model phi3 installation errors** Google the error log and install required depedencies.
---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

**
**models** I have tried various models: openai, gemini and local modeldel phi3. The local model can only generates english reponses cause it ứa trained based on English. 

---

## IV. Future Improvements (5 Points)

**Real-time data implements:** The provided data is stored in agents/dalat_travels_tools.py as fixed strings. Threrefore, I need to call the third API to get the real-time data.
**Fixed problem**: This solution only apply for Dalat, and it has no UI to interact with user, get prompt from user, query with fixed prompt. I need to add a UI to interact with user, get prompt from user.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
