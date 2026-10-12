---
date: 2019-01-10 22:59:33
authors:
  - gabriel
slug: you-need-to-write-tests
description: Writing unit tests at work should be one of your top priority!
---

# You need to write tests

Writing unit tests at work should be one of your top priority!

<!-- more -->

In my first ever programming job, I remember hearing about unit tests a lot, but I simply didn't get the importance of them : "Why do I need to waste time writing extra code to test my own code? I know how my code works!!"

It felt completely useless and also extremely boring. But boy, was I wrong! A few years later I progressively realised that unit tests are necessary in having a stable and ever-evolving professional code base.

## "Any code that isn't covered by unit tests is legacy code"

That's a bold statement, isn't it? I remember hearing it at a tech conference a while ago. For those who may not know, legacy code is basically code that we judge very hard to maintain and change, or even understand. Every tech company has it, to some extend. They're often due to change of mind, emergencies that we didn't clean later, or general bad maintainance of the code base.

But surely you would say, if I write some very clean code right now, it's not legacy code! Even without unit test, right?

Well, actually it is... or more exactly, it will be!

Because, let's say that you write a brand new shiny class and its purpose is very clear... What makes you think that Bob the new software engineer in 5 years will understand it? Especially if you're not around anymore? And what if in those 5 years a lot of bug fixes, edge cases, and extra methods were added in your class? Well, you have it! Congratulations, you created legacy code! Sure, it wasn't ugly at the start, but it became so in the long run!

## Understanding the purpose of tests

One problem is that junior developers tend to not understand the actual purpose for unit tests. That was my mistake too back in the days.

It's not really about testing right away that your new code works (although it can help you achieve that!). It's about writing a contract on how your code is supposed to behave and what's expected of it. By defining all the expected outcomes of your class / method / function, you simply show what the intent of your code is.

One of the main issue with software engineering is of time : code bases evolve and go through several teams of developers all with different ideas and new tech trends they want to try out. The code gets old, messy, and hard to understand.

Therefore, defining a contract that tells future developers what each part of the code was intended to do is fundamental.

It means that :

- new features added in the code can be done with more confidence as tests might break if bugs are introduced

- refactoring can be done more easily for the same reason

- unit tests can be read to give some context on what to expect (in case the production code isn't clear enough)
