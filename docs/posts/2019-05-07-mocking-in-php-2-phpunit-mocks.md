---
date: 2019-05-07 20:37:59
authors:
  - gabriel
slug: mocking-in-php-2-phpunit-mocks
description: How to use PHPUnit built-in mocking system
---

# Mocking in PHP #2: PHPUnit mocks

How to use PHPUnit built-in mocking system

<!-- more -->

As we've seen in the [previous article](2019-03-02-mocking-in-php-1-writing-your-own-mocks.md "Mocking in PHP #1: Writing your own mocks"), writing your own mocks is certainly a good way to understand how mocking works and why it's a powerful tool in the context of unit tests. However, writing custom mocks takes time and can generate a lot of code once your code base starts to grow.

Most developers use mocking tools or frameworks to avoid this issue.

PHPUnit comes with some mocking mechanism, so this can be a good place to start!

## Case study

Let's reuse our example from the previous article of the PostService class.

This class takes as dependencies a doctrine entity manager and a repository.

It also has two public methods that we will want to test :

- one to create a post

- one to retrieve a post from the DB

```php
<?php

namespace App;

use Doctrine\ORM\EntityManagerInterface;

class PostService
{
    /** @var EntityManagerInterface */
    private $entityManager;

    /** @var PostRepository  */
    private $postRepository;

    public function __construct(EntityManagerInterface $entityManager, PostRepository $postRepository)
    {
        $this->entityManager = $entityManager;
        $this->postRepository = $postRepository;
    }

    public function createPost(Post $post): void
    {
        $this->entityManager->persist($post);
        $this->entityManager->flush();
    }

    public function getPost(int $id): Post
    {
        /** @var Post|null $post */
        $post = $this->postRepository->find($id);
        if (is_null($post)) {
            throw new \RuntimeException('Post not found');
        }

        return $post;
    }
}
```

## Unit tests

This time, we will use the **createMock** method from PHPUnit to create our mocks.

This method takes the name of the class as an argument, and returns a mock version of that class.

Most mocking frameworks (including PHPUnit) works in a similar way that what we did when we created our own mocks:

- the mock extends our original class

- public methods are not doing anything by default (they usually simply returns null)

- we can override the behaviour we want for each public method

```php
<?php

namespace App\Tests\PHPUnit;

use App\Post;
use App\PostRepository;
use App\PostService;
use Doctrine\ORM\EntityManagerInterface;
use PHPUnit\Framework\MockObject\MockObject;
use PHPUnit\Framework\TestCase;

class PostServiceTest extends TestCase
{
    private const POST_ID = 1;

    /** @var PostRepository|MockObject */
    private $postRepository;

    /** @var EntityManagerInterface|MockObject */
    private $entityManager;

    /** @var PostService */
    private $service;

    public function setUp(): void
    {
        $this->postRepository = $this->createMock(PostRepository::class);
        $this->entityManager = $this->createMock(EntityManagerInterface::class);
        $this->service = new PostService($this->entityManager, $this->postRepository);
    }

    public function testGetPost(): void
    {
        $expected = new Post();

        $this->postRepository->method('find')
            ->with(self::POST_ID)
            ->willReturn($expected);

        $post = $this->service->getPost(self::POST_ID);

        $this->assertSame($expected, $post);
    }

    public function testGetPost_PostNotFound(): void
    {
        $this->expectException(\RuntimeException::class);

        $this->postRepository->method('find')
            ->with(self::POST_ID)
            ->willReturn(null);

        $this->service->getPost(self::POST_ID);
    }

    public function testCreatePost(): void
    {
        $post = new Post();

        $this->entityManager->expects($this->once())
            ->method('persist')
            ->with($post);

        $this->entityManager->expects($this->once())
            ->method('flush');

        $this->service->createPost($post);
    }
}
```

When testing **getPost**, we mock the behaviour of postRepository using *->method(...)->with(...)->willReturn(...).*

It means we can define what each method should return for a given set of parameters.

Furthermore, when testing **createPost**, we prefix the method mocking by a call to *->expects($this->once())*. This will perform an assertion that the call has been made once.

There are of course more options on what you can assert and mock (e.g. you can make a method throw an exception, you can verify successive calls to a method...). [PHPUnit documentation on mock](https://phpunit.de/manual/6.5/en/test-doubles.html#test-doubles.mock-objects "PHPUnit documentation on mock") is full of information on all the possibilities.
