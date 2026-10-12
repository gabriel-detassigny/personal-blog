---
date: 2021-04-03 13:48:36
authors:
  - gabriel
slug: design-pattern-3-decorator-pattern
description: A pattern with a similar purpose to inheritance, but with some advantages!
---

# Design Pattern #3: Decorator Pattern

A pattern with a similar purpose to inheritance, but with some advantages!

<!-- more -->

I have used the decorator design pattern a few times recently, and while it's simple and useful, it's surprisingly not that often applied.

Therefore, I decided to write a small post detailing how it works, and why you could potentially use it.

## What's the decorator pattern?

The concept of a decorator pattern is fairly simple: let's imagine that you already have an established concrete class (like a service) doing something and this class implements some interface. You want to add a piece of extra functionality to it but that work isn't a must-have, just something to add on top. You could either:

- add your changes to the existing class

- extend the class with a new child class

- use the **decorator pattern**: You create a new class that will implement the same interface, and receive the original class (i.e. the decorated class) as a parameter using [dependency injection](2018-12-06-design-pattern-2-dependency-injection.md).

Each option has its pros and cons, but let's see in practice how you would use the decorator pattern.

## Example

### Decorated class

Let's say we have a service that sends an email (this will be our decorated class) and it extends an interface:

```php
interface MailSenderInterface
{
    public function sendEmail(string $destination, string $subject, string $message): bool;
}

class MailSenderService implements MailSenderInterface
{
    public function sendEmail(string $destination, string $subject, string $message): bool
    {
        return mail($destination, $subject, $message);
    }
}
```

### Decorator class

Now, we realise that in some cases we want to log an error in case the mail failed to be sent. Let's use our decorator pattern to do that!

```php
class ErrorLoggerDecorator implements MailSenderInterface
{
    private MailSenderInterface $decorated;
    private LoggerInterface $logger;

    public function __construct(MailSenderInterface $decorated, LoggerInterface $logger)
    {
        $this->decorated = $decorated;
        $this->logger = $logger;
    }

    public function sendEmail(string $destination, string $subject, string $message): bool
    {
        if ($this->decorated->sendEmail($destination, $subject, $message)) {
            return true;
        }
        $this->logger->error('Failed to send e-mail to ' . $destination);

        return false;
    }
}
```

That's it! we inject our decorated class into it, use it to do the job of sending the email, and in case it failed we log an error using our application logger.

Now, you could say that we could have done that directly in the decorated class, but perhaps your mail sender service is used multiple times in your application and you want to log one specific instance only.

Also, this is more in line with [SOLID Principles](https://en.wikipedia.org/wiki/SOLID): each class does one thing only, and you're extending instead of modifying your existing code.

### Make your application use it

If your application is well structured, other parts of the code would hopefully already reference the interface instead of the decorated class. For example:

```php
class MailSendingController
{
    private MailSenderInterface $mailSender;

    public function __construct(MailSenderInterface $mailSender)
    {
        $this->mailSender = $mailSender;
    }

    public function sendEmail(array $params): void
    {
        $this->mailSender->sendEmail($params['dest'], $params['subject'], $params['message']);
    }
}
```

This means that you wouldn't have to change anything there. You simply need to inject the decorator into that controller:

```php
$decorator = new ErrorLoggerDecorator(new MailSenderService(), $logger);
$controller = new MailSendingController($decorator);
```

If you're using a framework, this might be done via configuration. In fact, Symfony actually has built-in support for [service decoration](https://symfony.com/doc/current/service_container/service_decoration.html) in its configuration making it even easier to set up.

### Chaining decorators

Let's add another decorator: In some parts of my application, I want to retry one more time sending the email if it failed.

We can add a new decorator for that:

```php
class RetryDecorator implements MailSenderInterface
{
    private MailSenderInterface $decorated;

    public function __construct(MailSenderInterface $decorated)
    {
        $this->decorated = $decorated;
    }

    public function sendEmail(string $destination, string $subject, string $message): bool
    {
        if ($this->decorated->sendEmail($destination, $subject, $message)) {
            return true;
        }

        return $this->decorated->sendEmail($destination, $subject, $message);
    }
}
```

Simple, isn't it?

You can then add this one on top of the other if needed.

## Why should I use this instead of inheritance?

While both cases studied above could have been solved with inheritance, inheritance has some limits and disadvantages that decorators can fix:

- if your service is declared as a **final class**, you won't be able to use inheritance. This is often the case with some 3rd party libraries, including some Symfony packages.

- You can chain your decorators however you like! To use our examples above: Maybe one part of your application wants to log error but try sending only the email once, maybe another one would like to send twice and log the error as well, etc...
