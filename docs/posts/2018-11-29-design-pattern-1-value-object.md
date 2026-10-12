---
date: 2018-11-29
authors:
  - gabriel
slug: design-pattern-1-value-object
description: Learn how and why to use this simple yet very effective design pattern!
---

# Design Pattern #1: Value Object

Learn how and why to use this simple yet very effective design pattern!

<!-- more -->

I named this article "*Design Pattern #1*" because I think it would be cool to write more of these in the future, but only time will tell if I actually commit to it...

In this article I will try to explain how the value object design pattern works and more importantly how you can use it!

First of all, I think this is a very nice pattern because it's equally simple to use and can be very powerful in keeping your code clean.

## Why do I need this?

I don't know about you, but one thing that annoys me about some design patterns is that you're never sure if you can actually use them in your day to day programming life! What's the point of learning them if you don't use them in the end?

Well, the good thing is that the value object design pattern is very easy to use and can be used in many situations!

Let's start with an example: Let's say your program contains an email address. You may want to make sure in various part of your system that a specific variable is actually an email address. You'll then have one of this at multiple places in your code :

```php
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    throw new Exception('Houston we have a problem!');
}
```

And that will work, but having it everywhere is a bit... annoying, no?

Now you may tell me "but I can put that in a function somewhere and call it everywhere I want!".

Sure, that will work, you could do this :

```php
function ensureIsEmail($email)
{
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new Exception('Invalid email: ' . $email);
    }
}

public function functionA($email)
{
    ensureIsEmail($email);
    functionB($email);
}

public function functionB($email)
{
    ensureIsEmail($email);
    // Do something else with $email
}

if (filter_var($email, FILTER_VALIDATE_EMAIL) !== false) {
    functionA($email);
}
```

See the problem? Everywhere you passes *$email*, you need to make sure it's still a valid email. Or you could try to remember if it's been checked before depending on context, but that could become very painful to track in a large system...

But what if instead you had a specific class that encapsulated your $email value? What if the value being in that class meant it was already validated?

You know where I'm going with this, value object is the answer! If you had such a class, you could do this:

```php
public function functionA(EmailAddress $email)
{
    functionB($email);
}

public function functionB(EmailAddress $email)
{
    // Do something else with $email
}

try {
  $email = new EmailAddress('myemail@example.com');
catch (Exception $e) {
  // Handle error here
}

functionA($email);
```

No more checking that the email address is valid! ...Well, not exactly, you still need to do it the first time you instantiate the value object, which means we'll check the value of the variable in the constructor. Let's go over that now.

## How can I write a value object class?

The rules of a value object are simple :

- all verification is done in the constructor

- if the value passed in the constructor is not valid, throw an exception

- the value object is immutable (otherwise we could change the value to a non valid one, and that would defeat its purpose)

- there should be a getter of some sort to access the value

Here is how our email address could look like :

```php
class EmailAddress
{
    private $value;

    public function __construct(string $value)
    {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid email: ' . $email);
        }
        $this->value = $value;
    }

    public function getValue(): string
    {
        return $this->value;
    }
}
```

Now, you can simply instantiate it the first time, catch the exception in case the value isn't valid, and if it is valid you can pass the object anywhere in your system and expect it to stay valid.

## How I can use my new shiny value object?

Now, let's have a more practical example on how to use it : Let's say you have an endpoint that sends a password reset email to a user. It means we'll have a controller that reads the parameter, and a service that sends the email.

Obviously I'll emit a lot of code and leave only the parts that we're interested in.

Our controller could look like this :

```php
class PasswordResetController
{
    private $service;

    public function __construct(PasswordResetService $service)
    {
        $this->service = $service;
    }

    public function sendPasswordResetEmail(string $emailParam)
    {
        try {
            $emailAddress = new EmailAddress($emailParam);
        } catch (InvalidArgumentException $e) {
            // Handle error somehow (display an error page, throw an exception...)
            throw new Exception('Invalid parameter ' . $emailParam);
        }
        $this->service->sendEmail($emailAddress);
    }
}
```

We can use the EmailAddress value object to verify the formatting of the parameter. Once it is done, we know the rest of the code will have a correctly formatted email address.

In case the email is not valid, we can handle the exception on the controller level and deal with it accordingly.

Now let's have a look at the service called by the controller :

```php
class PasswordResetService
{
    public function sendEmail(EmailAddress $emailAddress)
    {
        mail($emailAddress->getValue(), 'Password reset', 'Your link to your new password is...');
    }
}
```

This is obviously an overly simple service but you get the idea : the service expects a value object and therefore doesn't need to validate its format. It can then call the **getValue** method to retrieve its value.
