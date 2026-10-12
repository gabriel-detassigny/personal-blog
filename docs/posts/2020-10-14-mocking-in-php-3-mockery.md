---
date: 2020-10-14 19:19:55
authors:
  - gabriel
slug: mocking-in-php-3-mockery
description: How to use one of PHP's most popular mocking library
---

# Mocking in PHP #3: Mockery

How to use one of PHP's most popular mocking library

<!-- more -->

In previous articles, we've seen how it's possible to write your own mocks, and also how easier it is to use PHPUnit built-in mocking mechanism.

However, there are a few libraries dedicated to mocking in PHP land. Their popularities prove that while PHPUnit can work, it isn't always enough and its syntax can be rather confusing at times.

In this article, we'll demonstrate how to use [mockery.](https://packagist.org/packages/mockery/mockery "mockery")

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

## Installation

First, if you haven't already done so, you will need to install mockery using composer:

`composer require --dev mockery/mockery`

## Unit tests

```php
<?php

namespace App\Tests\Mockery;

use App\Post;
use App\PostRepository;
use App\PostService;
use Doctrine\ORM\EntityManagerInterface;
use Mockery;
use Mockery\Adapter\Phpunit\MockeryPHPUnitIntegration;
use Mockery\MockInterface;
use PHPUnit\Framework\TestCase;

class PostServiceTest extends TestCase
{
    use MockeryPHPUnitIntegration;

    private const POST_ID = 1;

    /** @var PostRepository|MockInterface */
    private $postRepository;

    /** @var EntityManagerInterface|MockInterface */
    private $entityManager;

    /** @var PostService */
    private $service;

    protected function setUp(): void
    {
        $this->postRepository = Mockery::mock(PostRepository::class);
        $this->entityManager = Mockery::mock(EntityManagerInterface::class);
        $this->service = new PostService($this->entityManager, $this->postRepository);
    }

    public function testGetPost(): void
    {
        $expected = new Post();

        $this->postRepository->expects('find')
            ->with(self::POST_ID)
            ->andReturn($expected);

        $actual = $this->service->getPost(self::POST_ID);

        $this->assertSame($expected, $actual);
    }

    public function testGetPost_PostNotFound(): void
    {
        $this->expectException(\RuntimeException::class);

        $this->postRepository->expects('find')
            ->with(self::POST_ID)
            ->andReturn(null);

        $this->service->getPost(self::POST_ID);
    }

    public function testCreatePost(): void
    {
        $post = new Post();

        $this->entityManager->expects('persist')->with($post);
        $this->entityManager->expects('flush');

        $this->service->createPost($post);
    }
}
```

Compared to PHPUnit mocks, we can note a few things:

- We use the static call to *Mockery::mock* to create a mock of the class passed as an argument.

- We use a trait named *MockeryPHPUnitIntegration* to tell PHPUnit to treat all Mockery's *expects* calls as assertions.

- In *testGetPost_PostNotFound*, we need to tell Mockery that the call to *find* should return null. If not, an error will be thrown by Mockery.

## Other functionalities

Mockery supports many useful additional features:

- Spies

- Partial mocks

- *allows* method let you define a desired outcome for a method call without requiring it to be called (compared to *expects*)

...and many more! Have a look at [their documentation](http://docs.mockery.io/en/latest/index.html "Mockery's documentation") if you are interested.
