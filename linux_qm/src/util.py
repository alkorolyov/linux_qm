import logging
import os
from uuid import uuid4


import py3Dmol
from rdkit import Chem
from rdkit.Chem import AllChem, rdChemReactions
from rdkit.Chem.MolStandardize import rdMolStandardize
from indigo import Indigo
indigo = Indigo()

# from rxnmapper import BatchedMapper
# rxn_mapper = BatchedMapper(batch_size=8)



def ind_rxn_map(rxn_smi):
    try:
        ind_rxn = indigo.loadReaction(rxn_smi)
        ind_rxn.automap("discard")
        return ind_rxn.smiles()
    except Exception as e:
        logging.warning(f'Failed to map reaction {rxn_smi}: {e}')


def normalize(smi):
    try:
        mol = Chem.MolFromSmiles(smi)
        lfc = rdMolStandardize.LargestFragmentChooser()
        mol = lfc.choose(mol)
        n = rdMolStandardize.Normalizer()
        mol = n.normalize(mol)
        u = rdMolStandardize.Uncharger()
        mol = u.uncharge(mol)
        return Chem.MolToSmiles(mol)
    except Exception as e:
        logging.warning(f'Failed to normalize smiles {smi}: {e}')

def check_amide_mapping(rxn_smi):
    try:
        rxn = rdChemReactions.ReactionFromSmarts(rxn_smi, useSmiles=True)
        rxn.Initialize()
        mapped_atoms = rxn.GetReactingAtoms()
    except:
        return False

    if len(mapped_atoms) != 2:
        return False
    if len(mapped_atoms[0]) != 1:
        return False
    if len(mapped_atoms[1]) != 2:
        return False

    if len(rxn.GetProducts()) > 1:
        return False

    if len(rxn.GetReactants()) != 2:
        return False

    amine, acid = rxn.GetReactants()

    # check for amine reacting atom
    amine_atom = amine.GetAtomWithIdx(mapped_atoms[0][0])
    if amine_atom.GetSymbol() != 'N':
        return False

    # check for neighbors of N in amine
    for nei in amine_atom.GetNeighbors():
        if nei.GetSymbol() not in ['H', 'C']:
            return False


    # check acid
    acid_ids = mapped_atoms[1]
    carbon_ids = [i for i in acid_ids if acid.GetAtomWithIdx(i).GetSymbol() == 'C']
    oxygen_ids = [i for i in acid_ids if acid.GetAtomWithIdx(i).GetSymbol() == 'O']
    others = [i for i in acid_ids if acid.GetAtomWithIdx(i).GetSymbol() not in ['C', 'O']]

    if others:
        return False
    if len(carbon_ids) != 1:
        return False
    if len(oxygen_ids) != 1:
        return False

    # other than acids
    carbon = acid.GetAtomWithIdx(carbon_ids[0])
    for nei in carbon.GetNeighbors():
        if nei.GetSymbol() not in ['O', 'C']:
            return False

    return True
# def rxn_map(rxn_smi):
#     clear_smi = re.sub(r':\d+','',  rxn_smi)
#     mapped_rxn = list(rxn_mapper.map_reactions([clear_smi]))[0]
#     return mapped_rxn

def load_smiles3D(smi: str, opt=False, num_conf=1):
    mol = Chem.MolFromSmiles(smi)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol)  # 3D coordinates
    if num_conf > 1:
        AllChem.EmbedMultipleConfs(mol, num_conf)
    if opt:
        AllChem.MMFFOptimizeMolecule(mol)
    mol.SetProp("smiles", Chem.CanonSmiles(smi))
    return mol


def draw3Dconfs(mol, autoalign=True, confIds=None, size=(600, 400)):
    if autoalign:
        AllChem.AlignMolConformers(mol)

    print('num conformers', mol.GetNumConformers())

    # Visualize using Py3Dmol
    viewer = py3Dmol.view(width=size[0], height=size[1])

    if not confIds:
        # all conformers
        confIds = [conf.GetId() for conf in mol.GetConformers()]

    for conf in mol.GetConformers():
        if conf.GetId() in confIds:
            mol_block = Chem.MolToMolBlock(mol, confId=conf.GetId())
            viewer.addModel(mol_block, "mol")

    viewer.setStyle({"stick": {}})
    # viewer.setBackgroundColor("black")
    viewer.zoomTo()
    viewer.show()

def _create_tmp_dir(tmp_root):
    uid = str(uuid4())
    tmp_path = f"{tmp_root}/{uid}"
    os.makedirs(tmp_path, exist_ok=True)
    return tmp_path
