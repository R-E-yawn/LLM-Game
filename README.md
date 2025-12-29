# Impostor.AI
<img width="418" height="589" alt="image" src="https://github.com/user-attachments/assets/d3dfa8eb-e381-472b-938d-ba3aa45a4de2" /> <img width="1262" height="667" alt="image" src="https://github.com/user-attachments/assets/d8906bb2-31c1-4e96-873d-e53cbda18be2" />

<img width="1261" height="676" alt="image" src="https://github.com/user-attachments/assets/8dd48399-07b0-47f9-ab7f-7bbf17057694" />


Key Technologies: 
- OpenAI GPT API
- Multi-agent LLM system
- Prompt chaining
- React
- Python
- FastAPI

Impostor.AI is an AI-powered social deduction game inspired by Among Us. Instead of observing player behavior during live gameplay, you take on the role of a detective interrogating four AI-powered suspects. One of them is the impostor who committed a murder on the spaceship, and your job is to figure out who's lying by cross-referencing their testimonies. Each suspect is powered by OpenAI's GPT models with distinct behavioral prompts—three are programmed to tell the truth based on what they witnessed, while one is designed to deceive, deflect, and fabricate alibis. You have 30 questions to interrogate the suspects before making your final accusation.

The game generates a unique narrative each session through a prompt chaining architecture. Rather than using a static scenario, the backend makes iterative LLM calls where each time period builds upon the context established by previous calls, creating 10 interconnected periods of events. After the timeline is generated, a final LLM call analyzes the complete event history to select which player had the best opportunity to commit the murder and generates the corresponding murder details. This chaining approach ensures narrative coherence—players move realistically between locations, witnesses corroborate each other's presence, and the murder event fits naturally into the established timeline.

The multi-agent system assigns each suspect a role-specific prompt architecture. Crewmate agents receive their personal event history and are instructed to answer truthfully, admitting uncertainty when they don't know something. The impostor agent receives both a cover story and the secret murder details, with instructions to never confess, deflect accusations, redirect suspicion toward others, and maintain internal consistency while fabricating alibis. When you interrogate a suspect, the system constructs a prompt containing their role instructions, personal event history, murder context (from their perspective), conversation history, and your current question, then sends it to OpenAI's API for completion.

The project is built with a React frontend for the interrogation interface and a Python FastAPI backend that handles game state management and LLM orchestration. To run locally, clone the repository, install dependencies for both frontend and backend, start the FastAPI server on port 8000, start the Vite dev server, and enter your OpenAI API key when prompted. The key is stored only in memory for the session. The game is won by carefully cross-referencing testimonies—asking each suspect where they were at specific times, verifying alibis against witness statements, and catching the impostor in contradictions that reveal their guilt.
