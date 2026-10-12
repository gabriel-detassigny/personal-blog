---
date: 2019-03-02 11:54:09
authors:
  - gabriel
slug: mocking-in-php-1-writing-your-own-mocks
description: A good way to vizualize how mocking works in the first place is to implement your own mocks
---

# Mocking in PHP #1: Writing your own mocks

A good way to vizualize how mocking works in the first place is to implement your own mocks

<!-- more -->

Mocking is a fundamental part of unit testing. Without mocks, you're stuck into writing tests that need to handle all dependencies of your class. Which sometimes means having to interact with the database, a file system, an API... It's simply way to complicated and is outside the scope of unit testing anyway.

In this series of articles called "Mocking in PHP", I will explore different ways of mocking your dependencies when writing PHPUnit test.

While definitely not the most common way of doing this, writing your own mocks can be a great way to understand what a mock is and what it does.

On the following articles, I will then go through different methods, such as :

- **PHPUnit mocks**: Their syntax isn't very straightforward but they come out of the box with PHPUnit without a need for any other package.

- **Mockery**: This is probably the most popular PHP mocking library right now.

- **Phake**: Another mocking library. My personal favourite.

## Case Study

First, let's define what we'll be testing here.

Let's say we have a service that is used by our application to interact with blog posts:

```php
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

It contains two methods :

- one to create a Post entity

- one to retrieve a Post by a given ID

Our service also has two [Injected dependencies](2018-12-06-design-pattern-2-dependency-injection.md "Design pattern: dependency injection"):

- [Doctrine](https://www.doctrine-project.org/ "Doctrine")'s entity manager. We need it for persisting our entities into the database.

- Our PostRepository, which is also a doctrine repository. We use that to search for entities.

## Unit tests

In order to test our PostService class, we will need three different classes :

- one mock class for the repository

- one mock class for the entity manager

- our test suite

### Mocking the repository

When writing our mock for the repository, we simply need to deal with the methods that our service will interact with, and see what possible outcome we want from our mock.

In this case, the service only uses one method from the repository : *find*.

Then, we have two different expected behavior we want to handle :

- an entity is returned

- null is returned

```php
namespace App\Tests\OwnMocks;

use App\Post;
use App\PostRepository;

class MockPostRepository extends PostRepository
{
    /** @var int */
    private $expectedId;

    /** @var Post */
    private $post;

    public function __construct(Post $post, int $expectedId)
    {
        $this->post = $post;
        $this->expectedId = $expectedId;
    }

    public function find($id, $lockMode = null, $lockVersion = null)
    {
        if ($id === $this->expectedId) {
            return $this->post;
        }

        return null;
    }
}
```

There are probably many ways to achieve that, but this is a good example.

First, our mock needs to extend the class that we're mocking. Without this, we would get an error that our mock isn't a PostRepository, as we type hinted it in the PostService constructor.

Then, you'll notice we're injecting a **post** and an **expectedId** into our mock constructor. Then, once we call **find**, if the **id** parameter is the expected one, we return our post. Otherwise we return null.

We can then test both behavior without any real repository implementations (no database calls or complicated logic).

### Mocking the entity manager

Now, let's have a look at the entity manager! In our PostService, you may have noticed that we actually inject the EntityManagerInterface. This means that our mock will need to implement the interface and all its methods. In this case, there is a lot of them! No problem though, we can simply leave all the ones we're not interested as empty.

```php
namespace App\Tests\OwnMocks;

use Doctrine\ORM\EntityManagerInterface;
use Doctrine\ORM\Query\ResultSetMapping;

class MockEntityManager implements EntityManagerInterface
{
    private $persistedObject = null;
    private $flushed = false;

    public function persist($object)
    {
        $this->persistedObject = $object;
    }

    public function flush()
    {
        $this->flushed = true;
    }

    public function isPersisted($object): bool
    {
        return $this->persistedObject === $object;
    }

    public function hasFlushed(): bool
    {
        return $this->flushed;
    }

    /** Defining all remaining EntityManager methods below */
    public function getCache() {}
    public function getConnection() {}
    public function getExpressionBuilder() {}
    public function beginTransaction() {}
    public function transactional($func) {}
    public function commit() {}
    public function rollback() {}
    public function createQuery($dql = '') {}
    public function createNamedQuery($name) {}
    public function createNativeQuery($sql, ResultSetMapping $rsm) {}
    public function createNamedNativeQuery($name) {}
    public function createQueryBuilder() {}
    public function getReference($entityName, $id) {}
    public function getPartialReference($entityName, $identifier) {}
    public function close() {}
    public function copy($entity, $deep = false) {}
    public function lock($entity, $lockMode, $lockVersion = null) {}
    public function getEventManager() {}
    public function getConfiguration() {}
    public function isOpen() {}
    public function getUnitOfWork() {}
    public function getHydrator($hydrationMode) {}
    public function newHydrator($hydrationMode) {}
    public function getProxyFactory() {}
    public function getFilters() {}
    public function isFiltersStateClean() {}
    public function hasFilters() {}
    public function find($className, $id) {}
    public function remove($object) {}
    public function merge($object) {}
    public function clear($objectName = null) {}
    public function detach($object) {}
    public function refresh($object) {}
    public function getRepository($className) {}
    public function getMetadataFactory() {}
    public function initializeObject($obj) {}
    public function contains($object) {}
    public function __call($name, $arguments) {}
    public function getClassMetadata($className) {}
}
```

We implement the two methods used by our service : **flush** and **persist**.

Then, as these methods don't return anything, we instead need the ability to check that they were correctly called.

To do so, I added two methods that returns boolean values : **isPersisted** and **hasFlushed**.

We then simply set variables in our flush and persist methods, and verify their values in our added boolean methods.

### Test suite

Now that we have our mocks, let's write our actual tests!

```php
namespace App\Tests\OwnMocks;

use App\Post;
use App\PostService;
use PHPUnit\Framework\TestCase;

class PostServiceTest extends TestCase
{
    private const EXPECTED_ID = 1;

    /** @var Post */
    private $expectedPost;

    /** @var MockPostRepository */
    private $postRepository;

    /** @var MockEntityManager */
    private $entityManager;

    /** @var PostService */
    private $service;

    public function setUp(): void
    {
        $this->expectedPost = new Post();
        $this->postRepository = new MockPostRepository($this->expectedPost, self::EXPECTED_ID);
        $this->entityManager = new MockEntityManager();
        $this->service = new PostService($this->entityManager, $this->postRepository);
    }

    public function testGetPost(): void
    {
        $post = $this->service->getPost(self::EXPECTED_ID);

        $this->assertSame($this->expectedPost, $post);
    }

    public function testGetPost_PostNotFound(): void
    {
        $this->expectException(\RuntimeException::class);

        $this->service->getPost(2);
    }

    public function testCreatePost(): void
    {
        $post = new Post();
        $this->service->createPost($post);

        $this->assertTrue($this->entityManager->isPersisted($post));
        $this->assertTrue($this->entityManager->hasFlushed());
    }
}
```

We create and inject our mocks via the setUp method of PHPUnit.

Then, we can test how our service methods behave using our mocks.
