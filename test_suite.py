import unittest
from intent_classifier import classify_intent

class TestIntentClassifier(unittest.TestCase):

    def test_coding_intent(self):
        self.assertEqual(classify_intent("How do I write a function in Python?"), "coding")
        self.assertEqual(classify_intent("I have an error in my Java code."), "coding")
        self.assertEqual(classify_intent("What is a good algorithm for sorting?"), "coding")

    def test_writing_intent(self):
        self.assertEqual(classify_intent("Can you proofread this email?"), "writing")
        self.assertEqual(classify_intent("Help me write a summary of this document."), "writing")
        self.assertEqual(classify_intent("What is a better way to phrase this sentence?"), "writing")

    def test_design_intent(self):
        self.assertEqual(classify_intent("What do you think of this UI design?"), "design")
        self.assertEqual(classify_intent("I need ideas for a new logo."), "design")
        self.assertEqual(classify_intent("How can I improve the user experience of my app?"), "design")

    def test_research_intent(self):
        self.assertEqual(classify_intent("What is the capital of France?"), "research")
        self.assertEqual(classify_intent("Find me some data on climate change."), "research")
        self.assertEqual(classify_intent("Who was the first person to walk on the moon?"), "research")

    def test_strategy_intent(self):
        self.assertEqual(classify_intent("How can I create a business plan?"), "strategy")
        self.assertEqual(classify_intent("What are the risks of this investment?"), "strategy")
        self.assertEqual(classify_intent("Help me develop a roadmap for my product."), "strategy")

    def test_empathy_intent(self):
        self.assertEqual(classify_intent("I'm feeling anxious about my presentation."), "empathy")
        self.assertEqual(classify_intent("My friend is going through a tough time."), "empathy")
        self.assertEqual(classify_intent("How can I be a better listener?"), "empathy")

    def test_default_intent(self):
        self.assertEqual(classify_intent("Hello, how are you?"), "default")
        self.assertEqual(classify_intent("What's the weather like today?"), "default")
        self.assertEqual(classify_intent("Tell me a joke."), "default")

if __name__ == '__main__':
    unittest.main()
