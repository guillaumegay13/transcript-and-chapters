# transcript-and-chapters
Create a transcript and chapters from an audio file (like a Podcast episode)

# How to Use

## Set up your API key
```bash
export OPENAI_API_KEY=your_key_here
```

## Add your audio file
Place your .mp3 file in the project directory and update MP3_FILE.

## Run the script
```bash
python main.py
```

## Get your results
Check the output files (transcript_ep1.txt and chapters_ep1.txt, or your chosen filenames).

# Example Output

For this podcast episode : https://podcasts.apple.com/fr/podcast/g%C3%A9n%C3%A9ration-ia/id1811120641?i=1000705826569

Here's the chapters txt file generated based on the raw mp3 :

```
0:00:00 - Améliorations et concurrents de ChatGPT
0:08:26 - Révolution des vidéos et tâches automatisées
0:16:51 - Révolution des modèles d'IA: Claude et Gemini
0:25:15 - L'avènement de Gemini: concurrence et progrès
0:33:37 - Mistral AI: Une success story française dans le domaine de l'IA
0:42:01 - Innovation et avancée technologique: l'impact de Groc et de l'IA sur les entreprises.
0:50:25 - Lucie, l'IA publique qui a fait un flop
```
