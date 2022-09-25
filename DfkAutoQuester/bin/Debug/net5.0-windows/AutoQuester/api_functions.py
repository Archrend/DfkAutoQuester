import requests
import json
import pandas as pd
import numpy as np
import datetime
from dateutil import tz
import time
import hero.hero_core as h_core
import meditation.meditation as meditation
from quests.utils import utils as quest_utils

#################################################################
def getHeroInfo(group,logger,rpc_server,hero_contract):
    try:
        string = ''
        for i in group:
            string = string + '"' + str(i) + '",'
        string = string[:-1]

        query = """query{
          heroes(where:{
            id_in:[%s]}) {
             id
            mainClass
            subClass
            rarity
            level
            xp
            currentQuest
            stamina
            staminaFullAt
            profession
            statBoost1
            statBoost2
            mining
            gardening
            foraging
            fishing
            status
            strength
            agility
            endurance
            wisdom
            dexterity
            vitality
            intelligence
            luck
            saleAuction {
                            id
                        }
            salePrice
            owner {
                    id
                   }
          }
        }""" % string
        logger.debug(query)

        url = 'https://defi-kingdoms-community-api-gateway-co06z8vi.uc.gateway.dev/graphql/'
        r = requests.post(url, json={'query': query})
        logger.debug(r.status_code)
        responses = pd.DataFrame(json.loads(r.text)['data']['heroes'])
        responses.set_index('id', inplace=True)
        responses['staminaMax'] = responses['stamina']
        responses['stamina'] = responses['staminaMax'] - (responses['staminaFullAt'] - datetime.datetime.utcnow().replace(
            tzinfo=tz.tzutc()).timestamp()) / 60 / 20
        responses['stamina'] = responses['stamina'].apply(np.floor)
        for i in responses[responses['stamina']>responses['staminaMax']].index:
            responses.at[i,'stamina'] = responses.at[i,'staminaMax']

        responses = responses.rename(
            columns={'strength': 'STR', 'agility': 'AGI', 'endurance': 'END', 'wisdom': 'WIS', 'dexterity': 'DEX',
                     'vitality': 'VIT', 'intelligence': 'INT', 'luck': 'LCK'})

        for hero in responses.index:
            tempP = pd.DataFrame(index=['STR','AGI', 'END', 'WIS', 'DEX', 'VIT', 'INT', 'LCK'])
            for stat in tempP.index:
                tempP.at[stat, 'value'] = responses.at[hero,stat]
                if responses.at[hero, 'statBoost1'] == stat:
                    tempP.at[stat, 'value'] = tempP.at[stat, 'value'] + 1
                if responses.at[hero, 'statBoost2'] == stat:
                    tempP.at[stat, 'value'] = tempP.at[stat, 'value'] + 3
            responses.at[hero, 'highestStat'] = tempP['value'].idxmax()
            responses.at[hero, 'highestStatN'] = tempP['value'].max()
            responses.at[hero, 'mining'] = responses.at[hero, 'mining']/10
            responses.at[hero, 'gardening'] = responses.at[hero, 'gardening']/10
            responses.at[hero, 'fishing'] = responses.at[hero, 'fishing']/10
            responses.at[hero, 'foraging'] = responses.at[hero, 'foraging']/10

        for i in responses.index:
            try:
                responses.at[i, 'saleAuction'] = responses.at[i, 'saleAuction']['id']
                responses.at[i, 'salePrice'] = float(responses.at[i, 'salePrice']) / 1000000000000000000
            except:
                responses.at[i, 'saleAuction'] = 0
                responses.at[i, 'salePrice'] = 0.0
        for i in responses.index:
            responses.at[i, 'owner'] = responses.at[i, 'owner']['id']

        responses.index = responses.index.astype(np.int64)
        return responses
    except Exception as e:
        logger.error("Getting API failed due to: %s" % e)
        # traceback.print_exc()
        logger.info("Using blockchain info instead")
        return getHeroInfoBlockchain(group,logger,rpc_server,hero_contract)
#################################################################
def getHeroInfoBlockchain(group,logger,rpc_server,hero_contract):
    while True:
        try:
            responses = pd.DataFrame(
                columns=['id','level','xp', 'staminaMax', 'stamina', 'staminaFullAt', 'profession', 'statBoost1', 'statBoost2',
                         'owner', 'currentQuest', 'mining', 'gardening', 'foraging', 'fishing', 'strength', 'agility',
                         'endurance', 'wisdom', 'dexterity', 'vitality', 'intelligence', 'luck'])
            responses.set_index('id', inplace=True)
            responses.index = responses.index.astype(np.int64)
            for i in group:
                hero = h_core.human_readable_hero(h_core.get_hero(hero_contract,i, rpc_server))
                responses.at[i, 'currentQuest'] = hero['state']['currentQuest']
                responses.at[i, 'profession'] = hero['info']['statGenes']['profession']
                responses.at[i, 'mainClass'] = hero['info']['class']
                responses.at[i, 'subClass'] = hero['info']['subClass']
                b1 = hero['info']['statGenes']['statBoost1']
                if b1 == 'strength':
                    responses.at[i, 'statBoost1'] = 'STR'
                elif b1 == 'agility':
                    responses.at[i, 'statBoost1'] = 'AGI'
                elif b1 == 'endurance':
                    responses.at[i, 'statBoost1'] = 'END'
                elif b1 == 'wisdom':
                    responses.at[i, 'statBoost1'] = 'WIS'
                elif b1 == 'dexterity':
                    responses.at[i, 'statBoost1'] = 'DEX'
                elif b1 == 'vitality':
                    responses.at[i, 'statBoost1'] = 'VIT'
                elif b1 == 'intelligence':
                    responses.at[i, 'statBoost1'] = 'INT'
                elif b1 == 'luck':
                    responses.at[i, 'statBoost1'] = 'LCK'
                b2 = hero['info']['statGenes']['statBoost2']
                if b2 == 'strength':
                    responses.at[i, 'statBoost2'] = 'STR'
                elif b2 == 'agility':
                    responses.at[i, 'statBoost2'] = 'AGI'
                elif b2 == 'endurance':
                    responses.at[i, 'statBoost2'] = 'END'
                elif b2 == 'wisdom':
                    responses.at[i, 'statBoost2'] = 'WIS'
                elif b2 == 'dexterity':
                    responses.at[i, 'statBoost2'] = 'DEX'
                elif b2 == 'vitality':
                    responses.at[i, 'statBoost2'] = 'VIT'
                elif b2 == 'intelligence':
                    responses.at[i, 'statBoost2'] = 'INT'
                elif b2 == 'luck':
                    responses.at[i, 'statBoost2'] = 'LCK'
                responses.at[i, 'level'] = hero['state']['level']
                responses.at[i, 'xp'] = hero['state']['xp']
                responses.at[i, 'staminaFullAt'] = hero['state']['staminaFullAt']
                responses.at[i, 'staminaMax'] = hero['stats']['stamina']
                responses.at[i, 'strength'] = hero['stats']['strength']
                responses.at[i, 'agility'] = hero['stats']['agility']
                responses.at[i, 'endurance'] = hero['stats']['endurance']
                responses.at[i, 'wisdom'] = hero['stats']['wisdom']
                responses.at[i, 'dexterity'] = hero['stats']['dexterity']
                responses.at[i, 'vitality'] = hero['stats']['vitality']
                responses.at[i, 'intelligence'] = hero['stats']['intelligence']
                responses.at[i, 'luck'] = hero['stats']['luck']
                responses.at[i, 'mining'] = hero['professions']['mining'] / 10
                responses.at[i, 'gardening'] = hero['professions']['gardening'] / 10
                responses.at[i, 'foraging'] = hero['professions']['foraging'] / 10
                responses.at[i, 'fishing'] = hero['professions']['fishing'] / 10
                responses.at[i, 'owner'] = h_core.get_owner(hero_contract,i, rpc_server)
            responses['stamina'] = responses['staminaMax'] - (
                    responses['staminaFullAt'] - datetime.datetime.utcnow().replace(
                tzinfo=tz.tzutc()).timestamp()) / 60 / 20
            responses['stamina'] = responses['stamina'].apply(np.floor)
            for i in responses[responses['stamina'] > responses['staminaMax']].index:
                responses.at[i, 'stamina'] = responses.at[i, 'staminaMax']
                
            responses = responses.rename(
                columns={'strength': 'STR', 'agility': 'AGI', 'endurance': 'END', 'wisdom': 'WIS', 'dexterity': 'DEX',
                         'vitality': 'VIT', 'intelligence': 'INT', 'luck': 'LCK'})

            for hero in responses.index:
                tempP = pd.DataFrame(index=['STR', 'AGI', 'END', 'WIS', 'DEX', 'VIT', 'INT', 'LCK'])
                for stat in tempP.index:
                    tempP.at[stat, 'value'] = responses.at[hero, stat]
                    if responses.at[hero, 'statBoost1'] == stat:
                        tempP.at[stat, 'value'] = tempP.at[stat, 'value'] + 1
                    if responses.at[hero, 'statBoost2'] == stat:
                        tempP.at[stat, 'value'] = tempP.at[stat, 'value'] + 3
                responses.at[hero, 'highestStat'] = tempP['value'].idxmax()
                responses.at[hero, 'highestStatN'] = tempP['value'].max()
            return responses
        except Exception as e:
            if(str(e) == "execution reverted: ERC721: owner query for nonexistent token"):
                raise Exception("Error: Hero not on blockchain")
            logger.error("Getting Blockchain info failed due to: %s" % e)
            logger.info("Retrying in 30s")
            time.sleep(30)
            continue
#################################################################
def getHeroQuest(hero_id,quester_version,logger):
    retry = 0
    while retry < 3:
        try:
            quest = quester_version.get_hero_quest(hero_id)
            return quest
        except Exception as e:
            retry += 1
            time.sleep(5)
            logger.info("getHeroQuest")
            logger.error("Getting API failed due to: %s, attempting again in 5 seconds" % e)
    raise Exception("Error Fetching API")
#################################################################
def getHeroQuestData(hero_id,quest_v1,logger):
    retry = 0
    while retry < 3:
        try:
            quest = quest_v1.get_quest_data(quest_utils.human_readable_quest(quest_v1.get_hero_quest(hero_id))['id'])
            return quest
        except Exception as e:
            retry += 1
            time.sleep(5)
            logger.info("getHeroQuestData")
            logger.error("Getting API failed due to: %s, attempting again in 5 seconds" % e)
    raise Exception("Error Fetching API")

#################################################################
def getActivateMeditations(address,rpc_server,logger,contract_address):
    retry = 0
    while retry < 3:
        try:
            current_meditations = meditation.get_active_meditations(address, rpc_server,contract_address)
            return current_meditations
        except Exception as e:
            retry += 1
            time.sleep(5)
            logger.info("getActivateMeditations")
            logger.error("Getting API failed due to: %s, attempting again in 5 seconds" % e)
    raise Exception("Error Fetching API")

#################################################################
def readyForLevelUp(hero_ids,responses,logger):
    heroes_ready_for_levelup = []

    xp_responses =  responses["xp"]
    current_level_responses = responses["level"]

    for hero_id in hero_ids:
        if int(xp_responses[hero_id]) >= int(meditation.xp_per_Level(current_level_responses[hero_id])):
            heroes_ready_for_levelup.append(hero_id)

    return heroes_ready_for_levelup

#################################################################
def returnHeroesQuesting(hero_ids,responses,logger):
    questing_hero_ids = []
    questing_responses = responses["currentQuest"]

    for hero_id in hero_ids:
        if(questing_responses[hero_id] != "0x0000000000000000000000000000000000000000"):
           questing_hero_ids.append(hero_id)
    return questing_hero_ids

#################################################################
def returnHeroesMeditation(hero_ids,rpc_server, logger, contract_address):
    retry = 0
    while retry < 3:
        try:
            meditiation_hero_ids = []

            for hero_id in hero_ids:
                if(meditation.get_hero_meditation(hero_id,rpc_server,contract_address) != None):
                    meditiation_hero_ids.append(hero_id)

            return meditiation_hero_ids
        except Exception as e:
            retry += 1
            time.sleep(5)
            logger.info("returnHeroesMeditation")
            logger.error("Getting API failed due to: %s, attempting again in 5 seconds" % e)
    raise Exception("Error Fetching API")
#################################################################
def enoughStam(responses,logger):
    return (responses['stamina'].min())
#################################################################

def didAnyReachStamP1(responses,stam,logger):
    stam = stam + 1
    logger.debug(responses['stamina'])
    logger.debug(responses['stamina'] >= stam)
    selection = responses[responses['stamina'] >= stam]
    return not selection.empty
#################################################################
def enoughStamSelection(responses,stam,logger):
    logger.debug(responses['stamina'])
    logger.debug(responses['stamina'] >= stam)
    return responses[responses['stamina'] >= stam]
#################################################################
def getHeroesInWallet(wallet_address,rpc_address,contract_address,logger):
    retry = 0
    while retry < 3:
        try:
            responses = h_core.get_users_heroes(contract_address,wallet_address,rpc_address)
            return responses
        except Exception as e:
            retry += 1
            time.sleep(5)
            logger.info("getHeroesInWallet")
            logger.error("Getting API failed due to: %s, attempting again in 5 seconds" % e)
    raise Exception("Error Fetching API")

#################################################################