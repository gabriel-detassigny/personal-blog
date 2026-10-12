---
date: 2018-12-02
authors:
  - gabriel
slug: going-frameworkless
description: Why I think everyone should try web developing without a framework
---

# Going Frameworkless

Why I think everyone should try web developing without a framework

<!-- more -->

About a year ago, I decided that I wanted to start my own tech blog at some point.

But that started in my head a long internal debate : What should I use to write my blog? Should I follow today's trend and use [medium.com](https://medium.com/)? Should I self-host a Wordpress blog?

After some thinking, I also realised that I didn't have any side project to work on at the moment, so I might as well write my own blog!

Then came the decision of which languages / frameworks to use? Ruby On Rails? PHP with Symfony? Laravel? Some new trendy language?

After some more thinking, I remembered a [PHP meetup](https://www.meetup.com/PHP-Dublin/) I went to in Dublin, where one of the member talked about writing a PHP application without any framework. That's it! Why not write my own blog in PHP 7, but no framework?

Of all the above options, I probably chose the longest to implement...

But in the end, I don't regret it at all!

This is my story of "going frameworkless" and why I think every PHP developer (and perhaps other devs too?) should try it at least once.

## Composer packages

![Composer](images/composer-1543725507.png)

First of all, I didn't exactly write everything from scratch... Sure, that would be an option as well but I'm not that masochist!

Instead, I used a few composer packages to handle specific tasks that I didn't want to implement myself :

- **Doctrine** was used for managing entities and DB persistency

- **Twig** for frontend

- [FastRoute](https://github.com/nikic/FastRoute) for request routing

- **phpdotenv** for managing env variables

... and a few other ones!

In the end, I spent a good amount of time just writing the glue between these various packages that I chose.

## What to write vs what to borrow

I think the general advice I would give is to write what you want to write yourself, and use a package for anything else you don't really feel like implementing.

For instance, I wrote my own container to manage my dependencies. I could have used an existing package for that, but I felt interested in writing my own implementation of the [PSR-11 Container Interface](https://www.php-fig.org/psr/psr-11/). My implementation is probably worse than most packages, but I'm still proud of it anyway! And believe it or not, I had a lot of fun writing it!

But if for some reasons you're wondering how you would go at writing your own DB persistency layer, then go ahead! You'll definitely learn a lot!

That's the first and probably the biggest reason I would advise in going frameworkless : *You'll have the opportunity to write code you would never write otherwise.*

## Performance

One other reason you might want to avoid using a framework could be performance. I really haven't looked at that too much when writing my blog to be honest, and probably I could spend some time optimising it.

However, you do end up with mostly code that you wrote yourself, or at least specific packages that you cherry picked. It means you know what to expect and you don't have a big overhead that a whole framework could introduce.

## Writing your own framework

Did you ever think about writing a framework yourself?

If you decide to go frameworkless, ask yourself this question in the end : Did you actually end up writing your own one?

You might actually really like the way you glued all the pieces necessary for your application/blog/website, why not try to make it a separate framework?

I haven't gone that far yet, and probably never will... but it's definitely the only time I've at least considered it. The code I write definitely has some pieces that looks shaped like the beginning of a framework.

I've met developers who attempted to write their own framework before. I truly believe that would be the best way to do so. You need a pet project to determine how your framework would look like!

## What I've learned

Just to be clear : I really like frameworks! They let you write projects with all the scaffolding already in place and good ones are usually well documented too. I'm not saying you should stop using them completely.

However, the learning experience I've had really makes me think that you should try once not using one!

It gave me the chance to write a lot of PHP code, to discover specific packages for specific tasks (e.g. routing is usually included in frameworks so I never had the chance to discover fast-route before), and also to simply have fun!

I don't think I would have enjoyed as much creating a medium account, or installing wordpress. Developing a blog in Laravel would have been okay, but a blog isn't that complicated so that would have been done quite quickly.

Instead, I spent some time thinking on how to implement specific parts of the system, how to have a container that behaves the way I would expect, how to handle errors, etc.

That would be my final reason for going frameworkless on a side project : Have you ever had a moment where you wanted to work on some programming side project but didn't have any new exciting idea? Well, maybe that could be the one! Just write a simple site or application but without any framework! I guarantee you will have some challenges and some fun!

If you're interested in having a look at the source code of this blog, [feel free](https://github.com/gabriel-detassigny/simple-blog).
