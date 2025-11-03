I see myself moving away from making clicks to do more typing recently. 

Since I started using CLI based coding agents, I feel reduced friction & increased productivity purely because these agents + MCP servers allowed me to avoid juggling between clicks & types on different apps.

I also feel that, my interaction experience with devices is slowly beginning to change. I've begun to realize that the medium of instructions to machines has evolved to natural language (chat + voice). 

---

A wonderful post that explains the scenario of the current job market and why it's important to have strong foundational knowledge of programming while also having the knowledge to use AI to work more efficiently than before. 

I use AI through Warp (my recent favorite coding agent) to auto-code. I just verify the generated code and re-prompt by pointing out what has to be improved and what should be removed. I keep on iterating in the above fashion until a solid codebase is laid out. Then, it's just about testing, re-factoring, sorting things out for deployment from development to staging to production.

---

I've been using many different LLMs since their advent yet I can only LOVE OpenAI & Anthropic. They never forget to impress. They just deliver!

Whenever I want to talk my emotions out, I always go to ChatGPT. I don't care about privacy. I don't care if they know me more than I know myself. I don't care if it's being manipulative. I need help. And ChatGPT does it. It reliable! It's has become my BEST COMPANION. It also helps with all my other needs to like assisting me in coding, deep search, etc.

And Claude, oh man, I literally can't find a suitable word to describe the greatness of their CLI. The time I used it was the time I fell in love with building (again). Though it's pricey. But, no other CLI based AI coding agents came close to what Claude did. Warp is promising & good yet I prefer Claude.

It might seem that I'm overly exaggerating them. But, I'm just honest. Many other models like Gemini, Grok, Qwen & DeepSeek are good too. Yet, the quality & reliability are at a trade off with those.

---

I've used many terminal based AI agents for vibe coding. But honestly, I had really great vibes with Warp ⚡. They bring a brand new coding experience to developers. 

I've been using it for a few days now and I'm simply amazed by how exciting it feels to write code. Maybe, it'll be the new way of writing code going into the future and I very much wish for it. 

The features that transformed my developer experience:
- First, it reduces my time of thinking about programming constructs and gives me time to focus more on my application itself.
- The way to prompt LLMs and the type of memory and workspace isolation.
- The universal input where you can input commands & prompts (text, img, video, URL, files, etc.)
- My most favourite one is the agent multi-threading where you can run many tasks parallely. 

---

I’m really into “vibe coding,” and it’s honestly so much fun!

Eager to ride the hype train, I kicked off one of my personal projects by using Claude code to bootstrap it. It did a smooth job setting everything up, which convinced me to vibe code the entire web app. The simple goal is to build a wrapper app around language and audio model providers using FastHTML.

After a few initial prompt iterations, here’s what I’ve noticed:
- The tool is incredible, but it’s pricey. It cost me about ~$4 just to finish the initial workflow of my app.
- Claude can do some stupid things when left to decide and act on its own with vague instructions.
- However, when I gave it clear instructions via prompting and a memory file (CLAUDE.md), it performed impressively.
- The trick is optimizing those prompts, instructions, and memory to cut costs while keeping Claude’s performance.

I’m going to keep vibe coding my app until it has the initial set of features I planned, though I won’t be too strict with my expectations. Waiting with my fingers crossed (🤞) to see the end result.

---

Ah, finally it's done. Ugh.. 😮‍💨 . I, here after, will never forget to push my changes to GitHub. Seriously, the python bindings for smoltoken should've been completed way before now. But then, I lost access to my personal computer and guess what, all my changes to the project was stuck with it. So people, even if you're about to die, just git push -> git commit and then RIP 💀.

Okay whatever, smoltoken is finally available on PyPI. Yet another byte pair encoder for your language models. Just pip install smoltoken and there you have it. Inspired by the famous tiktoken, built with rust, optimized for speed (as much as I can). Bring your data and train the vocabulary form scratch. Enjoy! 🍻 

---

If you are someone who is losing money on multiple AI subscriptions, then you might want to consider switching to Mammouth.

Mammouth AI is an AI aggregator that provides access to top proprietary and open-source conversational and image generation models while being affordable. I've been personally using it for a while and I really love it. It provides a friendly user-interface similar to Mistral's LeChat. I also have created assistants with specific instruction for different use-cases.

The product is still evolving. I miss a few features like quoting a part of response from the model in the follow up query and also I run into unknown errors now and then, but other than that it's amazing. 

I recommend that you check them.

---

Argh... Every post (atleast 9/10) I see is written by AI. Just my opinion, using LLMs to write your content, code or whatever, actually makes you dumb.

They do really help us alot when used in a proper way. I regularly use ChatGPT, Claude, Llama & Gemini (via NotebookLM) to extend my perspective, to learn new things and to research about something. But I often see people use it in a way that deteriorates their skills. Why, just why do people want to die so badly?

(At present) I only see AI as an assistant not as a replacement. So, unless you want to be replaced, use them to grow.

---

Smoltoken is now updated to support multi-threading using rayon which speeds up the training of tokenizer by almost 2x than the previous version.

Smoltoken is also now a part of https://github.com/smolorg by Maharshi Pandya.

Python bindings for smoltoken are on the way. You'll be able to train your tokenizer from scratch in Python without losing the performance that smoltoken offers. Stay tuned!

---

I've been working on extending OpenAI's tiktoken to enable training tokenizers on custom data, as it currently lacks this functionality. To address this gap, I created a Rust library — SmolToken designed for fast and efficient BPE tokenizer training from scratch.

The initial logic was inspired by the _educational.py implementation in tiktoken, which I ported and then significantly optimized. As a result, SmolToken is ~1.9x faster than the unoptimized baseline, making it suitable to train your own tokenizers when building language models.

The encoding and decoding implementations was borrowed from tiktoken. Hence it remains fast as it was. The library is still evolving — I plan to add multi-threading support using the rayon crate and Python bindings through PyO3.

I'm open-sourcing SmolToken and you can check it out on github: https://lnkd.in/grya5AGu. I’d love your feedback, and contributions are welcome! 

---

I haven't felt like a software engineer until I have had my hands on C++/CUDA. Reading through the CUDA documentation was really interesting. Moving from Python -> CUDA was 😮‍💨. It took me a while to write this matrix multiplication kernel only by referring the documentation. 

But, seriously, I have to write the whole behavior of the kernel in order to find a way to calculate indices based on the thread and block IDs. That was really tiresome. Have a look at the code in the below gist.

---

When you decide to train your own language model from scratch, before training a tokenizer you might want to consider using one of the pre-trained tokenizers from maybe GPT family's vocabulary or so, and prune the tokens from the bottom up. Because, they are trained on huge volumes of text and can handle the real world data better.

But one thing to note is that the pruned vocabulary might not be the best way to tokenize the data you have. Because, those pre-trained vocabulary is built with large variety of data including code, math & multiple languages while your dataset maybe biased to include more math/code/language.

Hence, analyze the pruned vocabulary and record the compression ratio it offers by encoding a sample of your data. If it's not something that satisfies you, then you can actually trained your own tokenizer.

---

It's nice to see how the hardware and software landscape of AI training & inference programs evolve over time. In 1990s, people didn't have much choice over the system or instruction set (programming language) to implemented neural networks, making them use C/C++ running on slow CPUs. Then with the Moore's law reaching its rapid elevation arc, we starting seeing more advanced chips like multi-core CPUs, GPUs, etc. and high level languages Python, Rust, Scala, etc. which made the development of AI models much faster & easier. 

Today, I'm overwhelmed by the no. of choices we have. So many frameworks, compilers and ASICs. However, it also enabled more people to involve in the process, building powerful tech that feels like magic. The preference of the stack people use vary across companies yet the goal is to improve our lives for the good. And it only makes me excited to be a part of this rapidly growing industry and be the first to experience a future we always have dreamt of.

---

I started learning machine learning during my college days. Back then, I used python and applied different statistical tools to model data. Fast forward to today, I now use python for building neural networks to model data. And the only thing that changed was interpretability. 

Everything I do now does feel like magic. But deep down it's just numbers, addition, multiplication and a bunch of mathematical functions. Whenever I imagine or try to visualize the training of a neural network in my head, I feel tingled. They seem like magic. 

At the end of the day, I feel like a magician trying to manipulate the numbers that were initialized at random by performing different mathematical operations on a set of numbers at hand to achieve a certain goal. 

I have no clue what I am doing yet I ❤️ what I do.