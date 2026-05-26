# Questions that will need to be asked

1. How do we get the historical names from the other team? - see the document `NameProvider/CONSUMER_QUICKSTART.md`
2. What are the requirements for a person to be able to be taken to the Temple? - see the document `TempleRequirements.md`
3. When you say "make them available", what does that mean? - The solution needs to provide a way to provide a name based on their gender (male or female)
4. How will the Ordinance Ready team want to get our Temple qualified names? - An http endpoint must be provided that can be called by the other team - specifying the following: 1. Gender 2. Number of names
5. Can you give me an idea of how many names we will be evaluating? - millions
6. How long would we be expected to save the qualified Temples persons? - indefinitly
7. Can you give me an idea of how often the Ordinance Ready team will get our names? - 24/7 at a rate of about 5,000 requests/second
8. After a name is retrieved by the Ordinance Ready team, do we need to keep the name in our system? - Yes, but the name should be marked somehow so that the same name is not returned more than once.
9. Does the receiving team need to notify us that the ordinance was received and accepted? No, not for the prototype