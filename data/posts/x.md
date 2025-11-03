I tried 
@OpenAI
's Codex CLI to code a fastHTML project in auto-pilot mode. 

Codex is an open-source command-line tool to use LLMs to read, modify, run code locally, speeding up dev, bug fixes, code comprehension. On Linux systems, Codex runs inside a container, providing a secure and sandboxed environment for making changes and executing code safely.

Being broke, I planned to use 
@GeminiApp
 models since they provide a generous free tier. But, it requires a few workarounds to setup it up on my Linux machine:

1. Generate Gemini API key via 
@googleaistudio
.
2. Export to `GEMINI_API_KEY` environment variable.
3. Ensure `pnpm` is installed.
4. Clone https://github.com/openai/codex repo.
5. Go to `codex/codex-cli/scripts` directory.
6. Edit `init_firewall.sh` to allow traffic to `http://generativelanguage.googleapis.com`.
7. Add `GEMINI_API_KEY` tto environment variables for the docker container in `run_in_container.sh` file.
8. Make scripts executable.
9. Build Docker container with `build_container.sh`.
10. Run CLI: `run_in_container.sh <query> --provider gemini --model gemini-2.5-flash-preview-04-17`.

---

Freedom and independence are different things. Freedom grants you the power to exercise your rights, while being independent means not relying on anything.

Independence is a myth. We all have a network and benefit from nearly every day. Without it, we might survive but cannot truly live.

---

The feeling of winning is the ultimate orgasm for me. While competing, I realized there can only be one best, depending on people's perspectives. Titles, awards, and recognition are just ways to show off victory. Real winning comes from feeling it - pure bliss, ultimate orgasm. If you cheated, you can show off, but deep down, the truth ruins your orgasm.

---

There are only two kinds of people: People who believe in tomorrow and those who don't.

For me, there's no fuckin' tomorrow.

---

There are only two things that people need to do, to accomplish anything in life: Decide & Act.

---

Be like water my friend:
The ability to learn, change and adapt is the greatest skill humanity has been gifted with. The smartest ones I've seen leverage this skill to its fullest.

---

Wasting time isn't always bad.

Taking a break is a waste of time. But energy exhaustion is real. Stopping to replenish our energy is a good use of time.

People don't have to be always productive. Spending time to learn how to be more productive is a good use of time.

---

When people face rejections they feel a want to know the reason. But, why aren't you curious about your acceptance/approvals?

Strive to improve, so not only the bad never happens but good keeps happening.

---

Learning to market & sell ourselves and our work is essential for any professional to be sustainably successful.

---

Knowing how to do something and having the ability to do it are different. The later is what is demanded of us as professionals.

---

Everything you do today, that defines who you are is a result of your decisions. And if they make you miserable you are pathetic to blame other things.

---

The greatest and most valuable thing that I realized in my life is that, I can't change anything in this world and no one really can. 

Yet in order to bring the change you want, study and work to set the right circumstances and hope that things change.

---

Be sensitive to the chages happening around you, but don't be reactive. Reaction happens subconsciously leaving no space for you to think. Observing, thinking and questioning every event of change will teach you greater things.

---

Everyone sucked at something before they became good at it.

---

Rationalism is not treating everything equal but treating everything as it is. Coz different things have different logics and reasons.

---

You can't generalize any group people as 'good' or 'bad'.

It depends on the people who is making the decision. It depends on their perception and perspective.

A good person may be bad for the bad ones and a bad person may appear good.
