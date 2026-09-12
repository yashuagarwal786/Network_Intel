# Network Intel: internal hackathon preparation pack

Prepared: 6 September 2026. Saara speaking material Roman-script Hinglish mein hai.

Tumhara immediate target: judges ko problem samajh aaye, ek working evidence chain clearly dikhe, aur team apne technical decisions defend kar sake. Selection guarantee nahi ho sakti, lekin preparation ko concrete proof ke around organize kar sakte ho.

## Pehle yeh 4 files use karo

1. **Network-Intel-Internal-Hackathon-Hinglish.pptx**: 8 main slides + 4 Q&A backup slides. Har slide ke Notes mein speaking script aur sources hain.
2. **Roadmap-and-Product-Understanding-Hinglish.md**: PS mapping, strengths, gaps, 7-day preparation plan, 48-hour fallback, evaluation checklist.
3. **Speech-and-Demo-Hinglish.md**: 30-second opening, timed pitch, 2:30 demo, short-round variant, failure recovery.
4. **Judges-QA-Hinglish.md**: 35 likely questions, concise spoken answers aur proof pointers.

## Abhi kya confirm karna baaki hai

- Official PS exact text / portal entry. Repo mein SIH26189 hai aur public mirrors same title dikhate hain, lekin official portal text directly verify nahi hua.
- College ka pitch/demo duration, marking rubric, mandatory slide limit aur submission format.
- Registered team name, members, college name, PS title/category/theme. Inko invent karke deck mein nahi dala gaya.

PPT ek presentation-ready working pitch hai. Official submission se pehle cover metadata aur mandated template apply karna zaroori ho sakta hai. Purana 6-slide SIH deck repo mein hai, lekin is request mein us template ko mandatory nahi maana gaya.

## Aaj ke verified observations

- Current branding **Network Intel** hai. Purane docs/screenshots mein **VEIL** naam hai. Deck mein reused screenshots ko previous synthetic run label kiya gaya hai.
- Live public link: https://veil-network-intel.vercel.app/
- Direct workspace: https://veil-network-intel.vercel.app/#/app
- Local primary demo: http://127.0.0.1:8000/#/app, backend running hona chahiye.
- `python -m pytest tests -q`: **101 passed, 2 dependency warnings, 22.99 seconds** in the current local environment. Test success real-world accuracy nahi hai.
- Root-level `pytest -q` ne `artifacts/launch-video/vendor/numpy` ke third-party tests collect karke missing `hypothesis` error diya. Product suite ko `tests` directory tak scope karne par pass hua. Rehearsal mein scoped command use karo.
- Vercel entrypoint `/tmp/veil-state` SQLite use karta hai. Hosted decisions durable multi-instance storage nahi hain. Local demo ko primary rakho, hosted persistence ko future hardening bolo.
- Dedicated influential-node / centrality ranking active backend mein verify nahi hui. Existing path search aur clustering feature ko iska replacement mat bolo.

## Tumhari core pitch line

“Network Intel alag reports, call records aur transactions ko source-linked network mein connect karta hai, taaki investigator har surfaced lead ka exact evidence inspect karke apna review record kar sake.”

Presentation ke end par judges ko yeh 3 things yaad rehni chahiye: working connection search, source tak traceability, aur investigator-controlled decisions.
