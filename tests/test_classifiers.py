"""Unit tests for Textpresso document classifiers"""

import unittest
import os
from textpresso_classifiers.classifiers import TextpressoDocumentClassifier, CasType, TokenizerType
from sklearn import svm
from sklearn.naive_bayes import GaussianNB

__author__ = "Valerio Arnaboldi"
__version__ = "1.0.1"


class TestTextpressoDocumentClassifier(unittest.TestCase):

    def setUp(self):
        this_dir = os.path.split(__file__)[0]
        self.training_dir_path = os.path.join(this_dir, "datasets")
        self.tpDocClassifier = TextpressoDocumentClassifier()

    def test_add_classified_docs_to_dataset(self):
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "pdf"),
                                                            file_type="pdf", category=2, recursive=True)
        self.assertTrue(len(self.tpDocClassifier.dataset.data) == 12)
        self.assertTrue(len(self.tpDocClassifier.dataset.target) == 12)

    def test_generate_training_and_test_sets(self):
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "pdf", "c_elegans"),
                                                            file_type="pdf", category=1)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        # call the function twice to re-generate dataset from previously split sets
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.assertGreater(len(self.tpDocClassifier.training_set.data), len(self.tpDocClassifier.test_set.data))

    def test_extract_features(self):
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        exception_caught = False
        try:
            self.tpDocClassifier.extract_features()
        except Exception:
            exception_caught = True
        self.assertTrue(exception_caught)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.tpDocClassifier.extract_features()
        self.assertTrue(self.tpDocClassifier.dataset is None)
        self.assertTrue(self.tpDocClassifier.test_set.tr_features is not None)
        self.tpDocClassifier.extract_features(tokenizer_type=TokenizerType.TFIDF, ngram_range=(1, 1),
                                              lemmatization=True, top_n_feat=50)
        self.assertTrue(self.tpDocClassifier.dataset is None)
        self.assertTrue(self.tpDocClassifier.test_set.tr_features is not None)
        self.tpDocClassifier.extract_features(tokenizer_type=TokenizerType.BOW, ngram_range=(1, 1),
                                              lemmatization=True, top_n_feat=50)
        self.assertTrue(self.tpDocClassifier.dataset is None)
        self.assertTrue(self.tpDocClassifier.test_set.tr_features is not None)

    def test_train_classifier(self):
        model = svm.SVC()
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        exception_caught = False
        try:
            self.tpDocClassifier.train_classifier(model=model)
        except Exception:
            exception_caught = True
        self.assertTrue(exception_caught)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.tpDocClassifier.extract_features(ngram_range=(1, 2))
        self.tpDocClassifier.train_classifier(model=model)
        self.assertEqual(len(self.tpDocClassifier.classifier.predict(self.tpDocClassifier.test_set.tr_features)),
                         len(self.tpDocClassifier.test_set.data))
        model = GaussianNB()
        self.tpDocClassifier.train_classifier(model=model, dense=True)

    def test_test_classifier(self):
        model = svm.SVC()
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        exception_caught = False
        try:
            self.tpDocClassifier.test_classifier()
        except Exception:
            exception_caught = True
        self.assertTrue(exception_caught)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.tpDocClassifier.extract_features(ngram_range=(1, 2))
        self.tpDocClassifier.train_classifier(model=model)
        test_results = self.tpDocClassifier.test_classifier()
        self.assertTrue(len(test_results) == 3)
        test_results = self.tpDocClassifier.test_classifier(test_on_training=True)
        self.assertTrue(len(test_results) == 3)
        model = GaussianNB()
        self.tpDocClassifier.train_classifier(model=model, dense=True)
        test_results = self.tpDocClassifier.test_classifier(dense=True)
        self.assertTrue(len(test_results) == 3)

    def test_remove_features(self):
        model = svm.SVC()
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.tpDocClassifier.extract_features(ngram_range=(1, 2), fit_vocabulary=True, transform_features=False)
        self.tpDocClassifier.remove_features([list(self.tpDocClassifier.vocabulary.keys())[0]])
        self.tpDocClassifier.extract_features(ngram_range=(1, 2), fit_vocabulary=False, transform_features=True)
        self.tpDocClassifier.train_classifier(model=model)
        self.assertEqual(len(self.tpDocClassifier.classifier.predict(self.tpDocClassifier.test_set.tr_features)),
                         len(self.tpDocClassifier.test_set.data))

    def test_prediction_single_file(self):
        model = svm.SVC()
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.generate_training_and_test_sets()
        self.tpDocClassifier.extract_features(ngram_range=(1, 1), fit_vocabulary=True, transform_features=True,
                                              top_n_feat=50)
        self.tpDocClassifier.train_classifier(model=model)
        prediction = self.tpDocClassifier.predict_file(file_path=os.path.join(self.training_dir_path, "pdf",
                                                                              "c_elegans", "WBPaper00004781.pdf"),
                                                       file_type="pdf")
        self.assertIsNone(prediction)
        prediction = self.tpDocClassifier.predict_file(file_path=os.path.join(self.training_dir_path, "cas",
                                                                              "c_elegans", "WBPaper00035071.tpcas.gz"),
                                                       file_type="cas_pdf")
        self.assertIsNotNone(prediction)
        prediction = self.tpDocClassifier.predict_file(file_path=os.path.join(self.training_dir_path, "cas",
                                                                              "animals", "animals-05-00396.tpcas.gz"),
                                                       file_type="cas_xml")
        self.assertIsNotNone(prediction)
        model = GaussianNB()
        self.tpDocClassifier.train_classifier(model=model, dense=True)
        prediction = self.tpDocClassifier.predict_file(file_path=os.path.join(self.training_dir_path, "cas",
                                                                              "animals", "animals-05-00396.tpcas.gz"),
                                                       file_type="cas_xml", dense=True)
        self.assertIsNotNone(prediction)

    def test_prediction_multiple_files(self):
        model = svm.SVC(gamma=0.1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.generate_training_and_test_sets()
        self.tpDocClassifier.extract_features(ngram_range=(1, 1), top_n_feat=50)
        self.tpDocClassifier.train_classifier(model=model)
        predictions = self.tpDocClassifier.predict_files(dir_path=os.path.join(self.training_dir_path, "pdf",
                                                                               "c_elegans"), file_type="pdf")
        self.assertFalse(all(predictions[1]))
        predictions = self.tpDocClassifier.predict_files(dir_path=os.path.join(self.training_dir_path, "cas",
                                                                               "c_elegans"), file_type="cas_pdf")
        self.assertTrue(all(predictions[1]))
        predictions = self.tpDocClassifier.predict_files(dir_path=os.path.join(self.training_dir_path, "cas",
                                                                               "animals"), file_type="cas_xml")
        self.assertTrue(all(predictions[1]))
        model = GaussianNB()
        self.tpDocClassifier.train_classifier(model=model, dense=True)
        predictions = self.tpDocClassifier.predict_files(dir_path=os.path.join(self.training_dir_path, "cas",
                                                                               "animals"), file_type="cas_xml",
                                                         dense=True)
        self.assertTrue(all(predictions[1]))

    def test_get_features_with_importance(self):
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.generate_training_and_test_sets()
        self.tpDocClassifier.extract_features(ngram_range=(1, 1), top_n_feat=50)
        features = self.tpDocClassifier.get_features_with_importance()
        self.assertTrue(len(features), 50)
        self.tpDocClassifier.extract_features(ngram_range=(1, 1))
        features = self.tpDocClassifier.get_features_with_importance()
        self.assertFalse(all([score for feat, score in features]))

    def test_save_to_file(self):
        self.tpDocClassifier.save_to_file("/tmp/classifier.pkl")
        self.assertTrue(os.path.isfile("/tmp/classifier.pkl"))
        self.tpDocClassifier.save_to_file("/tmp/classifier.pkl")
        self.assertTrue(os.path.isfile("/tmp/classifier.pkl"))

    def test_add_features(self):
        model = svm.SVC()
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "c_elegans"),
                                                            file_type="cas_pdf", category=1)
        self.tpDocClassifier.add_classified_docs_to_dataset(os.path.join(self.training_dir_path, "cas", "animals"),
                                                            file_type="cas_xml", category=2)
        self.tpDocClassifier.generate_training_and_test_sets(percentage_training=0.8)
        self.tpDocClassifier.extract_features(ngram_range=(1, 2), fit_vocabulary=True, transform_features=False)
        self.tpDocClassifier.add_features(["test"])
        self.tpDocClassifier.extract_features(ngram_range=(1, 2), fit_vocabulary=False, transform_features=True)
        self.tpDocClassifier.train_classifier(model=model)
        self.assertEqual(len(self.tpDocClassifier.classifier.predict(self.tpDocClassifier.test_set.tr_features)),
                         len(self.tpDocClassifier.test_set.data))


if __name__ == "__main__":
    unittest.main()
