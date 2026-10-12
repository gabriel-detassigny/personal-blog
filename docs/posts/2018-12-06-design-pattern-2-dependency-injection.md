---
date: 2018-12-06 06:32:07
authors:
  - gabriel
slug: design-pattern-2-dependency-injection
description: A very useful pattern to keep your application clean and enable unit testing
---

# Design Pattern #2: Dependency Injection

A very useful pattern to keep your application clean and enable unit testing

<!-- more -->

In the previous design pattern article, I went over the [Value Object](2018-11-29-design-pattern-1-value-object.md) pattern.

This time I will talk about how and why you should use dependency injection. Personally, this may be the design pattern that I use the most, and it's generally very common so if you don't know it, I strongly encourage you to learn about it!

I'm personally a bit annoyed about articles that uses cats and dogs, or wheels and cars as examples for this kind of stuff. It doesn't reflect what people usually work on. Therefore, I will instead use real life examples, mostly taken from [this blog's source code](https://github.com/gabriel-detassigny/simple-blog).

## What's dependency injection and how do I use it?

Let's say you have a class, and that class has some dependencies on other classes.

In our case, I have a service class to retrieve a blog post (such as the one you're reading right now) for a given ID, and its dependency is a doctrine repository that is in charge of connecting to the database and retrieve that post.

Well, one naive way to have your main class using your dependencies might be to declare its dependency inside it.

Like this :

```php
class PostViewingService
{
    /** @var PostRepository */
    private $repository;

    public function __construct()
    {
        // Create doctrine entity manager, and then get the repository from it
        $config = Setup::createAnnotationMetadataConfiguration([__DIR__ . '/Entity']);
        $em = EntityManager::create(['driver => 'pdo_mysql', 'user' => 'user'], $config);
        $this->repository = $em->getRepository(Post::class);
    }

    public function getPost(int $id): Post
    {
        /** @var Post $post */
        $post = $this->repository->find($id);

        if (!$post) {
            throw new PostNotFoundException("Post with ID {$id} was not found");
        }
        return $post;
    }
}

class PostRepository extends EntityRepository
{
}
```

That would work! You would be able to use your service, and it definitely has an instance of the repository created in its constructor. However, the constructor is now polluted with all the logic of how to create the repository.

This is how it would look instead using dependency injection :

```php
class PostViewingService
{
    /** @var PostRepository */
    private $repository;

    public function __construct(PostRepository $postRepository)
    {
        $this->repository = $postRepository;
    }

    public function getPost(int $id): Post
    {
        /** @var Post $post */
        $post = $this->repository->find($id);

        if (!$post) {
            throw new PostNotFoundException("Post with ID {$id} was not found");
        }
        return $post;
    }
}

class PostRepository extends EntityRepository
{
}
```

Isn't that cleaner? Now, of course you'll still need to create the repository somewhere beforehand to pass it into the service.

However, it makes your code way easier to read. And there are more advantages than just code readability too...

## Why should I use this?

### Centralize your instantiations

One reason you may want to use dependency injection is to have your instantiations written in one place only. Using our previous example, what would happen if I added another service that needs the PostRepository?

If the repository was instantiated in the services constructor as we did first, the new service would need to do the same! It means we would duplicate that ugly code to retrieve the repository from the doctrine entity manager.

However, using dependency injection, we can simply pass the same instance of the repository to both services, and avoid having duplicated code.

Having no duplication of that code means that if we ever need to change how that repository is created, we can change it in one place only.

Now, if you don't know how to handle these instantiations, I suggest having a look at containers, such as [this one](https://container.thephpleague.com/).

### Unit testing

Another huge advantage to dependency injection is that it allows us to unit test our code easily.

Indeed, if you wanted to test the behaviour of the *getPost* method on our service, you would need to have a database setup for the test, and therefore you would test both the service and its dependency (the repository). While this isn't necessarily a bad idea, it can be quite difficult and slow. Furthermore, it would be closer to an integration test than a unit test.

Instead, dependency injection allows us to use [Mocks](https://en.wikipedia.org/wiki/Mock_object).

Here is how tests could look like using PHPUnit and [Phake](https://github.com/mlively/Phake) as a mocking library :

```php
class PostViewingServiceTest extends TestCase
{
    /** @var PostViewingService */
    private $service;

    /** @var PostRepository */
    private $repository;

    public function setUp()
    {
        $this->repository = Phake::mock(PostRepository::class);
        $this->service = new PostViewingService($this->repository);
    }

    public function testGetPost_NotFound(): void
    {
        $this->expectException(PostNotFoundException::class);

        Phake::when($this->repository)->find(self::POST_ID)->thenReturn(null);

        $this->service->getPost(1);
    }

    public function testGetPost(): void
    {
         $post = new Post();
         Phake::when($this->repository)->find(self::POST_ID)->thenReturn($post);

        $result = $this->service->getPost(1);

        $this->assertSame($post, $result);
    }
```

Here we create a mock of the repository and inject it into our service. This means we don't need any database at all!

We can then define the mocks behaviour in our two test scenarios :

- if the repository returns null, the service method should throw an exception

- if the repository returns a *Post* entity, the service method should return it

If you're not too familiar with unit tests and mocks, I strongly suggest having a look at them as they're very big parts of software engineering.
