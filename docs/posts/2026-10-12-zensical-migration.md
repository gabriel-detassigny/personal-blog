---
date: 2026-10-12
authors:
  - gabriel
slug: zensical-migration
description: This blog was migrated to Zensical... and boy did Claude made this easy!
---

# Zensical Migration

This blog was migrated to Zensical... and boy did Claude made this easy!

<!-- more -->

## Previous Stack

This blog was built years ago, using a basic custom CMS I built called [simple-blog](https://github.com/gabriel-detassigny/simple-blog). Both the blog and the CMS were never intended to be more than some fun side projects, and they never went beyond that.

That custom CMS was built in pure PHP, with a few composer packages cherry-picked here and there. 

It provided a basic admin UI, and required some maintenance which I admittedly didn't do much as the blog quickly died down ...also having kids broke all motivation to write blog posts or do side projects for a while!

## The dilemma

For a while, I was wondering what to do with this blog... no one cares about this blog except me. No one is really reading this except me, years later.

The problem is maintaining an old custom stack with an admin access was a security risk. And yet I liked having this around, for me to revisit my thoughts years prior.

So what should I do? Delete the blog completely? Leave it as is?

Migrating it to an easier, more manageable tool seemed to be the best middle-ground.

## Zensical

Well, a couple of years ago, I started using [Material for Mkdocs](https://squidfunk.github.io/mkdocs-material/) at work for a wiki, and I really liked it.

Recently, there was a split in the Mkdocs community: Mkdocs is moving to a 2.0 version that's not backward compatible with most extensions. 

Because of that, [Zensical](Zensical.org/) was created as a spiritual successor which is backward-compatible.

If you're not familiar with Zensical/Mkdocs, they basically allow writing blogs/wiki articles as markdown files, and provide tooling to generate your site as basic HTML/CSS/JS. The result is very fast loading times, and no real security risks.

So that ticks all the boxes.

But you might be wondering (who am I kidding, no one is reading this), why am I doing this only now if I discovered Mkdocs years ago?

## Claude Code

Well, the elephant in the room nowadays in any tech conversation is AI, of course.

One thing I realised lately is how easy it now is to actually tackle the backlog of side project ideas I just never had the motivation to go through, thanks to LLMs.

Another thing I realised once I decided to try that is how quickly I (well, Claude) got that done! It really took about **30 min total** from the moment I explained the migration plan to the moment the new version was deployed live. 

Before AI, this would have taken me between 5 to 10 hours.

...what a world we live in!
