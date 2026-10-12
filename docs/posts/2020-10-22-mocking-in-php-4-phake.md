---
date: 2020-10-22 19:56:44
authors:
  - gabriel
slug: mocking-in-php-4-phake
description: A simple to use and yet powerful mocking library
---

# Mocking in PHP #4: Phake

A simple to use and yet powerful mocking library

<!-- more -->

In previous articles, we've seen how it's possible to write your own mocks, and also how easier it is to use PHPUnit built-in mocking mechanism. We've then finally looked at one of the most popular PHP mocking library: Mockery.

We'll now look at an alternative one called [Phake](https://github.com/mlively/Phake). We will compare the two and what their pros and cons are.

Phake is certainly less famous than Mockery, however it has a slightly different approach to mocking in some cases. It's worth noting that it's heavily inspired by [Mockito](https://site.mockito.org), a Java mocking library.

## Case study

In order to compare these libraries appropriately, let's reuse our example from the previous articles.

The following PostService class takes as dependencies a doctrine entity manager and a repository.

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

Just like with Mockery, Phake can be installed with composer:

`composer require --dev phake/phake`

Now that it's installed, let's have a look at unit testing this service class.

## Unit tests

```php
<?php

namespace App\Tests\Phake;

use App\Post;
use App\PostRepository;
use App\PostService;
use Doctrine\ORM\EntityManagerInterface;
use Phake;
use Phake_IMock;
use PHPUnit\Framework\TestCase;

class PostServiceTest extends TestCase
{
    private const POST_ID = 1;

    /** @var PostRepository|Phake_IMock */
    private $postRepository;

    /** @var EntityManagerInterface|Phake_IMock */
    private $entityManager;

    /** @var PostService */
    private $service;

    protected function setUp(): void
    {
        $this->postRepository = Phake::mock(PostRepository::class);
        $this->entityManager = Phake::mock(EntityManagerInterface::class);
        $this->service = new PostService($this->entityManager, $this->postRepository);
    }

    public function testGetPost(): void
    {
        $expected = new Post();
        Phake::when($this->postRepository)->find(self::POST_ID)->thenReturn($expected);

        $actual = $this->service->getPost(self::POST_ID);

        $this->assertSame($expected, $actual);
    }

    public function testGetPost_PostNotFound(): void
    {
        $this->expectException(\RuntimeException::class);

        $this->service->getPost(self::POST_ID);
    }

    public function testCreatePost(): void
    {
        $post = new Post();

        $this->service->createPost($post);

        Phake::verify($this->entityManager)->persist($post);
        Phake::verify($this->entityManager)->flush();
    }
}
```

We can notice a few similarities with Mockery:

- we use a static call to *Phake::mock* to instantiate our mocks.

- we can define behaviours fairly easily for each mock's methods.

However, there are some differences in the approach and syntax:

- Phake doesn't need to include any PHP trait to be able to make assertions in PHPUnit (compared to Mockery's *MockeryPHPUnitIntegration* trait)

- We use *Phake::when* to define an expected outcome of a method (return statement, throwing an exception...)

- In *testGetPost_PostNotFound*, we didn't define any expected outcome. That's because by default Phake methods will return null, which is what we wanted here.

- *Phake::verify* is used to assert an excepted call has been made to the mock. This is a fairly big difference compared to Mockery for two reasons:

1. Mockery uses the same call to the *expects* method to both define an expected outcome and verify that a call was made.

2. *Phake::verify* is called **after** the method call takes place, just like a regular PHPUnit assertion. This is in my opinion way more logical.

I personally prefer Phake's syntax than Mockery's. It's more straightforward, the distinction between *Phake::when* and *Phake::verify* gives a clearer intent, and verifying calls at the end of the test is more instinctive.

This is however a matter of personal preferences, as both Mockery and Phake present similar functionalities.

Here is a link to [Phake's documentation](https://phake.readthedocs.io/en/latest/index.html "Phake's documentation") if you are interested.
