# from copy import deepcopy
# from unittest.mock import patch
#
# from django.core.exceptions import ValidationError
# from django.test import TestCase
#
# from compounds.models import Odorant
#
#
# class MockPubChemPyObject:
#     def __init__(self, synonyms, cid=1234):
#         self.synonyms = synonyms
#         self.cid = cid
#
#
# class CompoundModelTestCase(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         super(CompoundModelTestCase, cls).setUpClass()
#         cls.cpd_data = {'cas_number': '26252-11-9', 'cid_number': 1234,
#                         'smiles': 'CCCCCC(O)C(/C)=C/CC', 'iupac_name': '(e)-4-methyldec-3-en-5-ol', }
#         cls.compound = Odorant.objects.create(**cls.cpd_data)
#         cpd_data2 = deepcopy(cls.cpd_data)
#         cpd_data2.update({'cas_number': '123-456-78', 'trade_name': 'Undecavertol', 'supplier': 'Giv.'})
#         cls.compound2 = Odorant.objects.create(**cpd_data2)
#     #
#     # def test_cas_number_regex_validator(self):
#     #     cpd_data = deepcopy(self.cpd_data)
#     #     cpd_data.update({'cas_number': '12345678'})
#     #     compound = Compound(**cpd_data)
#     #     with self.assertRaises(ValidationError):
#     #         compound.save()
#
#     def test_cas_number_max_length(self):
#         max_length = self.compound._meta.get_field('cas_number').max_length
#         self.assertEqual(max_length, 20)
#
#     @patch('odorants.models.compound.pcp.get_compounds')
#     def test_synonyms_cached_property(self, pcp_patch):
#         synonyms = ['4-Methyldec-3-en-5-ol', '81782-77-6', 'Undecavertol', '3-Decen-5-ol',
#                     '4-methyl-(E)-4-methyldec-3-en-5-ol', '(E)-4-methyl-3-decen-5-ol', 'EINECS 279-815-0', 'figovert']
#         pcp_patch.return_value = [MockPubChemPyObject(synonyms)]
#         self.assertEqual(self.compound.synonyms, ', '.join(synonyms))
#
#     @patch('odorants.models.compound.pcp.get_compounds')
#     def test_synonyms_cached_property_handles_key_error(self, pcp_patch):
#         pcp_patch.return_value = []
#         self.assertEqual(self.compound2.synonyms, 'n/a')
#
#     def test_structure_url_property(self):
#         self.assertEqual(self.compound.structure_url,
#                          'https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid={}&amp;t=l'.format(
#                              self.compound.cid_number))
#
#     @patch('odorants.models.compound.pcp.get_compounds')
#     def test_save_method_generates_cid_number(self, pcp_patch):
#         pcp_patch.return_value = [MockPubChemPyObject('synonyms', cid=5678)]
#         data = deepcopy(self.cpd_data)
#         data.update({'cid_number': '', 'cas_number': '123-345-678'})
#         compound = Odorant.objects.create(**data)
#         self.assertEqual(compound.cid_number, 5678)
#
#     @patch('odorants.models.compound.pcp.get_compounds')
#     def test_save_method_handles_no_cid_number_found(self, pcp_patch):
#         pcp_patch.side_effect = IndexError
#         data = deepcopy(self.cpd_data)
#         data.update({'cid_number': ''})
#         compound = Odorant(**data)
#         with self.assertRaises(ValidationError):
#             compound.save()
#
#     def test_save_method_raises_validation_error_if_incomplete_data(self):
#         compound = Odorant(cas_number='123-456-78')
#         with self.assertRaises(ValidationError):
#             compound.save()
#
#     def test_supplier_mixin_trade_name_max_length(self):
#         max_length = Odorant._meta.get_field('trade_name').max_length
#         self.assertEqual(max_length, 20)
#
#     def test_supplier_mixin_trade_name_verbose_name(self):
#         verbose_name = Odorant._meta.get_field('trade_name').verbose_name
#         self.assertEqual(verbose_name, 'Trade name')
#
#     @patch('odorants.models.compound.pcp.get_compounds')
#     def test_supplier_clean_field_method(self, pcp_patch):
#         pcp_patch.return_value = [MockPubChemPyObject('synonyms', cid=5678)]
#         data = self.cpd_data.copy()
#         data.update({'supplier': Odorant.supplier_choices[0][0]})
#         compound = Odorant(**data)
#         with self.assertRaises(ValidationError):
#             compound.save()
#
#     def test_substructure_matches_for_valid_matching_smiles_string(self):
#         output = Odorant.substructure_matches('CCCCCC(O)')
#         self.assertIn(self.compound.id, [a.id for a in output])
#         self.assertIsNone(Odorant.substructure_matches('invalid_smiles'))
#
#     def test_str_method(self):
#         self.assertEqual(str(self.compound), self.compound.iupac_name)
#         self.assertEqual(str(self.compound2), '{} ({}) | {}'.format(
#             self.compound2.trade_name, self.compound2.supplier, self.compound2.iupac_name))
#
#     def test_get_absolute_url(self):
#         self.assertEqual(self.compound.get_absolute_url(), '/odorants/compound/{}'.format(self.compound.id))
