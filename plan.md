# Architecture Plan

This is an overview of what will become the architecture of this project. The idea is that each module in the chain provides a generic interface, so they can be swapped out for alternative modules that provie the same functionality (E.G. to change the STT or TTS engine used).

1. **Record Audio**
    
    Recording starts when noise is detected, and stops when silence resumes. This audio is then passed on down the chain.

2. Turn the audio into words with a Speech to Text engine (STT).
    
    I plan to initially write a module that uses Mozilla's Deep Speech project.

3. Process and clean up this text (I.E. replace the word "comma" with a ",").
    
    This should be as simple as a chain of python functions that find / replace parts of the text.

4. Interpret the meaning of the text.
    
    This is by far the hardest part. In the long term, I might look into machine learning for this, but for now, I'll draw inspiration from the Jasper FLOSS voice assistent.

5. Deligate, based on the user's intent, the text to a module to handle the user's request.
    
    This module will have access to the user's information, as well as a channel to communicate further with the user.

These modules will also be available:

* **A user profile** to store module settings and the user's personal info.
* **Notification features** to allow modules to notify the user of events.
* **Direct audio APIs** for recording and playback. This could be adapted for music / radio, VOIP calls, etc.

