---
date: 2021-06-25 08:35:07
authors:
  - gabriel
slug: safe-refactoring-split-a-class-into-smaller-ones
description: A step-by-step guide on how to refactor big chunks of code using unit tests
---

# Safe Refactoring: split a class into smaller ones

A step-by-step guide on how to refactor big chunks of code using unit tests

<!-- more -->

Refactoring is hard! You most likely want to refactor old spaghetti code that you may or may not understand. There is a risk that you break everything in the process because of the complexity and potential edge cases that you didn't think about.

There are multiple ways to refactor old code and it also depends on what kind of code we're looking at improving (multiple classes and modules? a single class? old procedural code?).

In this guide, I will explain my general process when specifically looking at refactoring a single large class with the aim to split it into smaller ones. More importantly, I will explain how to do it in a **safe way** that should hopefully give you enough confidence to deploy your new changes without breaking anything.

## Case study

Let's imagine we have the following class we wish to refactor:

```php
namespace App\Controller;

use App\Post;
use App\PostRepository;
use Psr\Log\LoggerInterface;

class PostController
{
    private PostRepository $repository;
    private LoggerInterface $logger;

    public function __construct(PostRepository $postRepository, LoggerInterface $logger)
    {
        $this->repository = $postRepository;
        $this->logger = $logger;
    }

    public function getPostData(array $params): string
    {
        if (!isset($params['id'])) {
            throw new \InvalidArgumentException('Missing id parameter');
        }

        $id = (int) $params['id'];
        if ($id <= 0) {
            throw new \InvalidArgumentException('Invalid id parameter');
        }

        /** @var Post|null $post */
        $post = $this->repository->find($id);
        if (is_null($post)) {
            $this->logger->warning("Post with $id was not found");
            throw new \RuntimeException("Post with $id was not found");
        }

        return json_encode([
            'id' => $post->getId(),
            'text' => $post->getText()
        ]);
    }
}
```

It's a fairly large controller for a homemade API. It does a lot of things:

- it verifies the validity of the ID parameter and throws an exception in case it's not valid

- it uses Doctrine's repository to fetch the post entity.

- if the repository fails to get the data, it logs an error, and throws a runtime exception

- finally, if all went fine, it returns a json encoded response of the post data

Now, you may tell me "Well my work examples are more complex than that!" and you would be right... But obviously I keep the example simple enough so that it's not too complicated to explain the process. But the concept should be the same regardless.

## Unit test coverage

Now that we know roughly what our class does, the first thing to do (if not already available) is to cover its behaviour with unit tests! We'll be using **PHPUnit** for the tests and **Mockery** to mock the dependencies.

```php
namespace App\Tests\Controller;

use App\Controller\PostController;
use App\Post;
use App\PostRepository;
use Mockery;
use Mockery\Adapter\Phpunit\MockeryPHPUnitIntegration;
use PHPUnit\Framework\TestCase;
use Psr\Log\LoggerInterface;

class PostControllerTest extends TestCase
{
    use MockeryPHPUnitIntegration;

    private const POST_ID = 1;

    private PostRepository $repository;
    private LoggerInterface $logger;
    private PostController $controller;

    protected function setUp(): void
    {
        $this->repository = Mockery::mock(PostRepository::class);
        $this->logger = Mockery::mock(LoggerInterface::class);

        $this->controller = new PostController($this->repository, $this->logger);
    }

    /**
     * @dataProvider invalidParamsDataProvider
     */
    public function testGetPostDataThrowsErrorForInvalidParams(array $params, string $message): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage($message);

        $this->controller->getPostData($params);
    }

    public function invalidParamsDataProvider(): array
    {
        return [
            'Id is missing' => [[], 'Missing id parameter'],
            'Id is null' => [['id' => null], 'Missing id parameter'],
            'Id is set to zero' => [['id' => 0], 'Invalid id parameter'],
            'Id is set to a string' => [['id' => 'invalid'], 'Invalid id parameter']
        ];
    }

    public function testGetPostDataThrowsErrorIfPostNotFound(): void
    {
        $this->repository->allows('find')->with(self::POST_ID)->andReturn(null);

        $errorMessage = 'Post with id ' . self::POST_ID . ' was not found';

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessage($errorMessage);

        $this->logger->expects('warning')->with($errorMessage);

        $this->controller->getPostData(['id' => 1]);
    }

    public function testGetPostDataReturnsJsonEncodedPostData(): void
    {
        $expected = '{"id":1,"text":"some text from the post"}';

        $post = Mockery::mock(Post::class);
        $post->allows('getId')->andReturn(self::POST_ID);
        $post->allows('getText')->andReturn('some text from the post');

        $this->repository->allows('find')->with(self::POST_ID)->andReturn($post);

        $actual = $this->controller->getPostData(['id' => 1]);

        $this->assertJsonStringEqualsJsonString($expected, $actual);
    }
}
```

You should try to cover all paths of your code. In this example, we make sure to cover:

- invalid parameters (using a [data provider](https://phpunit.readthedocs.io/en/9.5/writing-tests-for-phpunit.html?highlight=data%20provider#data-providers))

- error handling for a post not found

- the successful scenario: the post is retrieved and formatted in JSON

If you want to ensure that all paths are properly covered, several metrics and tools could potentially help you:

- [code coverage](https://phpunit.readthedocs.io/en/9.5/code-coverage-analysis.html)

- [mutation testing](https://infection.github.io/guide/)

But of course manually looking at it may be enough, depending on the size and complexity of the class.

## Refactoring

We're now in a position where we've defined our expected behaviour (with unit tests) and can therefore validate if our refactor will be successful.

There are many ways we could go at simplifying this controller code, but here is my take on it:

- the parameter validation could be taken out and done in a [value object](2018-11-29-design-pattern-1-value-object.md).

- there is too much logic of doctrine repository and logging for a simple controller. Let's build a service that deals with that instead.

First, here is the PostId value object:

```php
namespace App\Value;

class PostId
{
    private int $id;

    public function __construct(array $params)
    {
        if (!isset($params['id'])) {
            throw new \InvalidArgumentException('Missing id parameter');
        }

        if ((int) $params['id'] <= 0) {
            throw new \InvalidArgumentException('Invalid id parameter');
        }

        $this->id = (int) $params['id'];
    }

    public function getId(): int
    {
        return $this->id;
    }
}
```

It includes all our check for the parameters that the controller used to do.

Now let's add a post service that deals with fetching the post using doctrine, and logging a warning if it's not found:

```php
namespace App;

use App\Value\PostId;
use Psr\Log\LoggerInterface;

class PostService
{
    private PostRepository $repository;
    private LoggerInterface $logger;

    public function __construct(PostRepository $repository, LoggerInterface $logger)
    {
        $this->repository = $repository;
        $this->logger = $logger;
    }

    public function getPost(PostId $postId): Post
    {
        /** @var Post|null $post */
        $post = $this->repository->find($postId->getId());
        if (is_null($post)) {
            $this->logger->warning("Post with id {$postId->getId()} was not found");
            throw new \RuntimeException("Post with id {$postId->getId()} was not found");
        }

        return $post;
    }
}
```

Perfect!

Now we can simplify our controller to use these two classes:

```php
namespace App\Controller;

use App\PostService;
use App\Value\PostId;

class PostController
{
    /** @var PostService */
    private PostService $postService;

    public function __construct(PostService $postService)
    {
        $this->postService = $postService;
    }

    public function getPostData(array $params): string
    {
        $postId = new PostId($params);
        $post = $this->postService->getPost($postId);

        return json_encode([
            'id' => $post->getId(),
            'text' => $post->getText()
        ]);
    }
}
```

Now, that's an easy to read controller! We could also take out the json formatting into a separate class, but that will do for the purpose of this exercise.

## Updating the tests

If you try running the tests now, it will fail because the controller dependencies have changed!

However, none of our logic actually has been modified: the code is doing the same thing as before.

This is probably the most important step, and yet if the refactor is done right, it's the simplest:

Instead of directly start writing tests for the new classes, and completely rewrite the existing ones, we need to slightly change the controller tests to prove that it still works. To do so, we'll only change the dependencies but without mocking them! Let it actually use the PostService properly, but we'll keep mocking the logger and the repository as before.

Our only change should therefore be to modify the **PostController** instanciation in the **setUp** method:

```php
$this->controller = new PostController(new PostService($this->repository, $this->logger));
```

That's it! The tests still pass! We've now refactored everything and we're fairly confident that the behaviour hasn't changed.

## What next?

Well, you could leave it like that, but most likely you may want to start writing tests for the **PostService** and then simplify the **PostControllerTest** by mocking the service and removing any mentions of the logger and repository. That way, not only your production code, but also your tests are simplified.
