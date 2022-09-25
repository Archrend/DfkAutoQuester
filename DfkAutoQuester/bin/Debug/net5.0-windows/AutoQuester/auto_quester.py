import json
from lib2to3.pgen2 import token
import math
from posixpath import split
import sys
import time
import datetime
import logger_functions
import api_functions
from web3 import Web3
import quests.quest_v1 as quest_v1
import quests.quest_v2 as quest_v2
from quests.utils import utils as quest_utils
from quests.professions import fishing,foraging,gardening,minning
from quests.training import arm_wrestling,game_of_ball,dancing,puzzle_solving,darts,helping_the_farm,alchemist_assistance,card_game
import hero.hero_core as h_core
import json
import dex.uniswap_v2_router as market_place_router
import dex.erc20 as tokens
import warnings
import meditation.meditation as meditation
import auctions.hero.sale_auctions as Auction
import MarketAbi
import dex.master_gardener as gardens
import dex.uniswap_v2_pair as pool
import dex.erc20 as erc20
import traceback
import numpy as np
import telegram_handler

 ##################################################################################################################################
# classes
class heroController:
    def __init__(self, account, hero_id):
        self.hero_id = hero_id
        self.checkup_time = time.time()
        self.quest_address = "0x0000000000000000000000000000000000000000"
        account.heroControllers.append(self)

    def setCheckUpTime(self, new_time):
        self.checkup_time = new_time 

class accountQuestManager:
    ##################################################################################################################################
    # Account Setup
    def __init__(self, key):
        # Settings inital variables
        self.key = key
        self.tx_timeout = 30
        self.rpc_server = "https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc"
        self.chain_id = 53935
        self.quest_contract_address = '0xE9AbfBC143d7cef74b5b793ec5907fa62ca53154'
        self.native_token = "0x04b9dA42306B023f3572e106B11D82aAd9D32EBb"
        self.gas_name = "JEWEL"
        self.gas_name_item = "CVGAS"
        self.wrapped_gas = "0xCCb93dABD71c8Dad03Fc4CE5559dC3D89F67a260"
        self.hero_contract_address = h_core.CRYSTALVALE_CONTRACT_ADDRESS
        self.gas_price_gwei = settings_json[int(index)]["OtherAccountSettings"]["DFKGWEI"]
        self.foraging_contract_address = foraging.QUEST_CONTRACT_ADDRESS_V2_CV
        self.fishing_contract_address = fishing.QUEST_CONTRACT_ADDRESS_V2_CV
        self.mining_contract_address = minning.GOLD_QUEST_CONTRACT_ADDRESS_V2_CV
        self.gardening_contract_address = gardening.QUEST_CONTRACT_ADDRESSES_CV
        self.str_contract_address = arm_wrestling.QUEST_CONTRACT_ADDRESS_CV
        self.int_contract_address = alchemist_assistance.QUEST_CONTRACT_ADDRESS_CV
        self.wis_contract_address = puzzle_solving.QUEST_CONTRACT_ADDRESS_CV
        self.lck_contract_address = card_game.QUEST_CONTRACT_ADDRESS_CV
        self.agi_contract_address = game_of_ball.QUEST_CONTRACT_ADDRESS_CV
        self.vit_contract_address = helping_the_farm.QUEST_CONTRACT_ADDRESS_CV
        self.end_contract_address = dancing.QUEST_CONTRACT_ADDRESS_CV
        self.dex_contract_address = darts.QUEST_CONTRACT_ADDRESS_CV
        self.meditation_contract_address = '0xD507b6b299d9FC835a0Df92f718920D13fA49B47'
        self.rune_address = '0x75E8D8676d774C9429FbB148b30E304b5542aC3d'
        self.monka_address = '0xCd2192521BD8e33559b0CA24f3260fE6A26C28e4'
        self.market_spending_address = '0x3C351E1afdd1b1BC44e931E12D4E05D6125eaeCa'
        self.tokens = tokens.ITEMS_CV
        self.auction_address = "0xc390fAA4C7f66E4D62E59C231D5beD32Ff77BEf0"
        self.max_gardeners = len(self.gardening_contract_address)*6
        self.max_miners = 18
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_server))
        self.account_address = self.w3.eth.account.privateKeyToAccount(self.key).address
        self.heroes = api_functions.getHeroesInWallet(self.account_address, self.rpc_server,self.hero_contract_address,logger)
        self.questV1 = quest_v1.Quest(self.rpc_server, logger)
        self.questV2 = quest_v2.Quest(self.rpc_server,self.quest_contract_address, logger)
        self.heroControllers = []
        self.gardening_jewel = 0
            
        # Contains all the accounts heroes seperated into professions
        self.gardeners = []
        self.foragers = []
        self.fishers = []
        self.miners = []

        self.arm_wrestling = []
        self.game_of_ball = []
        self.dancing = []
        self.puzzle_solving = []
        self.darts = []
        self.helping_the_farm = []
        self.alchemist_assistance = []
        self.card_game = []

        # Contains all the accounts heroes which are current questing seperated into professions
        self.questing_gardeners = []
        self.questing_miners = []
        self.questing_foragers = []
        self.questing_fishers = []

        self.questing_arm_wrestling = []
        self.questing_game_of_ball = []
        self.questing_dancing = []
        self.questing_puzzle_solving = []
        self.questing_darts = []
        self.questing_helping_the_farm = []
        self.questing_alchemist_assistance = []
        self.questing_card_game = []

        #Contains all Heroes to be put on auction
        self.tavern_heroes = settings_json[int(index)]["TavernSettings"]["SellingHeroIds"]

        logger.info("obtaining api values for heroes")
        # Aquires all the accounts heroes and seperates them into profession groups
        if len(self.heroes)!= 0:
            hero_api = api_functions.getHeroInfo(self.heroes,logger,self.rpc_server,self.hero_contract_address)
        else:
            hero_api = None
        for hero_id in self.heroes:
            hero_questing = len(api_functions.returnHeroesQuesting([hero_id],hero_api,logger)) > 0
            if(settings_json[int(index)]["TrainingSettings"]["Enabled"] == True and
              (((hero_api ['gardening'][hero_id] >= settings_json[int(index)]["TrainingSettings"]["MinGardeningProfSkill"] or len(self.gardeners) >= self.max_gardeners) and hero_api ['profession'][hero_id] == "gardening") or
               ((hero_api ['mining'][hero_id] >= settings_json[int(index)]["TrainingSettings"]["MinMiningProfSkill"] or len(self.miners) >= self.max_miners) and hero_api ['profession'][hero_id] == "mining") or
               (hero_api ['fishing'][hero_id] >= settings_json[int(index)]["TrainingSettings"]["MinFishingProfSkill"] and hero_api ['profession'][hero_id] == "fishing") or
               (hero_api ['foraging'][hero_id] >= settings_json[int(index)]["TrainingSettings"]["MinForagingProfSkill"] and hero_api ['profession'][hero_id] == "foraging")) and
                hero_api ['highestStatN'][hero_id] > settings_json[int(index)]["TrainingSettings"]["MinStatRequirement"]):

                if(hero_api ['highestStat'][hero_id] == "STR"): 
                    self.arm_wrestling.append(hero_id) 
                    if hero_questing: self.questing_arm_wrestling.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "AGI"): 
                    self.game_of_ball.append(hero_id)
                    if hero_questing: self.questing_game_of_ball.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "END"): 
                    self.dancing.append(hero_id)
                    if hero_questing: self.questing_dancing.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "WIS"): 
                    self.puzzle_solving.append(hero_id)
                    if hero_questing: self.questing_puzzle_solving.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "DEX"): 
                    self.darts.append(hero_id)
                    if hero_questing: self.questing_darts.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "VIT"): 
                    self.helping_the_farm.append(hero_id)
                    if hero_questing: self.questing_helping_the_farm.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "INT"): 
                    self.alchemist_assistance.append(hero_id)
                    if hero_questing: self.questing_alchemist_assistance.append(hero_id)
                if(hero_api ['highestStat'][hero_id] == "LCK"): 
                    self.card_game.append(hero_id)
                    if hero_questing: self.questing_card_game.append(hero_id)
                continue

            else:
                if(hero_api ['profession'][hero_id] == "gardening"): 
                    self.gardeners.append(hero_id) 
                    if hero_questing: 
                        self.questing_gardeners.append(hero_id)   

                elif(hero_api ['profession'][hero_id] == "mining"): 
                    self.miners.append(hero_id)
                    if hero_questing: self.questing_miners.append(hero_id)

                elif(hero_api ['profession'][hero_id] == "fishing"): 
                    self.fishers.append(hero_id)
                    if hero_questing: self.questing_fishers.append(hero_id)

                elif(hero_api ['profession'][hero_id] == "foraging"): 
                    self.foragers.append(hero_id)
                    if hero_questing: self.questing_foragers.append(hero_id)

        logger.info("Obtained heroes professions, seperating into groups and assigning controllers")
        # Seperates all heroes into their respective profession control group
        self.gardening_groups = self.seperateIntoControlGroups(self.gardeners,2,hero_api)

        self.mining_groups = self.seperateIntoControlGroups(self.miners,6,hero_api)
        self.foraging_groups = self.seperateIntoControlGroups(self.foragers,6,hero_api)
        self.fishing_groups = self.seperateIntoControlGroups(self.fishers,6,hero_api)

        self.arm_wrestling_groups = self.seperateIntoControlGroups(self.arm_wrestling,6,hero_api)
        self.game_of_ball_groups = self.seperateIntoControlGroups(self.game_of_ball,6,hero_api)
        self.dancing_groups = self.seperateIntoControlGroups(self.dancing,6,hero_api)
        self.puzzle_solving_groups = self.seperateIntoControlGroups(self.puzzle_solving,6,hero_api)
        self.darts_groups = self.seperateIntoControlGroups(self.darts,6,hero_api)
        self.helping_the_farm_groups = self.seperateIntoControlGroups(self.helping_the_farm,6,hero_api)
        self.alchemist_assistance_groups = self.seperateIntoControlGroups(self.alchemist_assistance,6,hero_api)
        self.card_game_groups = self.seperateIntoControlGroups(self.card_game,6,hero_api)

    def seperateIntoControlGroups(self, group, max_group_size, responses):
        overall_group = []
        current_group = []

        for i in range(0,len(group),1):

            this_heroController = heroController(self,group[i])
            this_heroController.quest_address = responses['currentQuest'][group[i]]
            current_group.append(this_heroController)

            if(len(current_group) == max_group_size or i == len(group)-1):
                overall_group.append(list.copy(current_group))
                current_group.clear()

        return overall_group

    def refreshHeroes(self):
        # gets heroes in wallet
        heroes_check = api_functions.getHeroesInWallet(self.account_address, self.rpc_server,self.hero_contract_address,logger)

        # Checks for new heroes
        for new_hero_id in heroes_check:
            if new_hero_id not in self.heroes:
                logger.info("new hero detected, remaking acount")
                self.__init__(self.key) 
                return

        # Checks for heroes removed from the account
        for old_hero_id in self.heroes:
            if old_hero_id not in heroes_check:
                logger.info("hero has been removed, remaking acount")
                self.__init__(self.key) 
                return

    ##################################################################################################################################
    # Start Quest Functions
    def StartQuestV2(self,quest_contract,heroes,stam, level):
        retry = 0
        while retry < 5:
            try:
                self.questV2.start_quest(quest_contract, heroes, stam, level, self.key, self.w3.eth.getTransactionCount(self.account_address),self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout)

                time.sleep(3)

                return True
            except Exception as e:
                # traceback.print_exc()
                logger.error("Starting quest failed due to: %s [%s] " %(e,heroes))
                retry = retry + 1
                if retry < 3:
                    logger.info("Retry number: %s" % retry)
                    time.sleep(5)
        return False
   
    ##################################################################################################################################
    # Mediation Functions
    def StartMeditation(self, hero_id, stats):
        retry = 0
        while retry < 5:
            try:
                logger.info("Attempting start meditation: " + str(hero_id))
                meditation.start_meditation(hero_id,stats[0],stats[1],stats[2],meditation.ZERO_ADDRESS,self.key,self.w3.eth.getTransactionCount(self.account_address),self.gas_price_gwei+(retry*(self.gas_price_gwei/10)),self.tx_timeout,self.rpc_server,logger,self.meditation_contract_address)
                return True
            except Exception as e:
                retry = retry + 1
                if(str(e) == "execution reverted: ERC20: burn amount exceeds allowance" or str(e) == "execution reverted: ERC20: insufficient allowance"):
                    logger.info("Burn failed, setting spending limits on ritual items")

                    approve_contract_runes = self.w3.eth.contract(address=self.rune_address,abi=tokens.ABI)
                    approve_contract_monkas = self.w3.eth.contract(address=self.monka_address,abi=tokens.ABI)
                    approve_contract_native_token = self.w3.eth.contract(address=self.native_token,abi=tokens.ABI)
                    self.ApproveSpendingLimit(approve_contract_monkas,self.meditation_contract_address)
                    self.ApproveSpendingLimit(approve_contract_runes,self.meditation_contract_address)
                    self.ApproveSpendingLimit(approve_contract_native_token,self.meditation_contract_address)
                else:
                    if(str(e) == "execution reverted: ERC20: transfer amount exceeds balance"):
                        logger.info("meditation failed to start, not enough native token (eg. jewel/crystal)")
                        break
                    elif(str(e) == "execution reverted: ERC20: burn amount exceeds balance"):
                        logger.info("meditation failed to start, not enough runes")
                        break

                    logger.info("meditation failed to start, trying a different hero: "+str(e))
                    if retry < 5:
                        logger.info("Retry number: %s" % retry)
                        time.sleep(5)
        return False

    def CompleteMeditation(self,hero_id):
        retry = 0
        while retry < 5:
            try:
                logger.info("Attempting complete meditation: " + str(hero_id))
                meditation.complete_meditation(hero_id,self.key,self.w3.eth.getTransactionCount(self.account_address),self.gas_price_gwei+(retry*(self.gas_price_gwei/10)),self.tx_timeout,self.rpc_server,logger,self.meditation_contract_address)
                time.sleep(3)
                for this_heroController in self.heroControllers:
                    if this_heroController.hero_id == hero_id:
                        this_heroController.setCheckUpTime(time.time())
                        break
                logger.info("Meditation completed!")
                return True
            except Exception as e:
                if str(e) == "execution reverted: no meditation":
                    logger.info("Meditation completed!")
                    return True
                logger.error("Completing meditation failed due to: %s [%s] " %(e,hero_id))
                retry = retry + 1
                if retry < 5:
                    logger.info("Retry number: %s" % retry)
                    time.sleep(5)
        logger.info("Complete meditation failed")
        return False

    ##################################################################################################################################
    # Blockchain Functions
    def ApproveSpendingLimit(self, token_contract, spender_address):
        logger.info("Attempting Increase Spending limit")
        retry = 0
        while retry < 3:
            try:
                tx = token_contract.functions.approve(Web3.toChecksumAddress(spender_address), int(10**57)).buildTransaction({'from': self.account_address,'gasPrice':  self.w3.toWei(self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 'gwei'), 'nonce': self.w3.eth.getTransactionCount( self.account_address)})
                logger.info("Signing transaction")
                signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
                self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                logger.info("Transaction successfully sent !")

                tx_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash=signed_tx.hash, timeout=180,
                                                                    poll_latency=2)  
                logger.info("Transaction mined !")
                logger.info("Spending Limit increased !")
                break

            except Exception as e:
                retry += 1
                logger.error("Spending Limit Increase Transaction Failed: " + str(e) + " retrying in 5 seconds")
                time.sleep(5)

    def SetApprovalForAll(self, token_contract, to_address):
        logger.info("Attempting To Set Approval")
        retry = 0
        while retry < 3:
            try:
                tx = token_contract.functions.setApprovalForAll(Web3.toChecksumAddress(to_address), True).buildTransaction({'from': self.account_address,'gasPrice':  self.w3.toWei(self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 'gwei'), 'nonce': self.w3.eth.getTransactionCount( self.account_address)})
                logger.info("Signing transaction")
                signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
                self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                logger.info("Transaction successfully sent !")

                tx_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash=signed_tx.hash, timeout=180,
                                                                    poll_latency=2)  
                logger.info("Transaction mined !")
                logger.info("Approval Set !")
                break

            except Exception as e:
                retry += 1
                logger.error("Setting Approval Transaction Failed: " + str(e) + " retrying in 5 seconds")
                time.sleep(5)

    def SendItems(self, token_amount, sending_token_contract, sending_token_symbol, sending_token_address, to_address):
        logger.info("Attempting Transfer " + str(token_amount * (10 ** (-1 * tokens.decimals(sending_token_address , self.rpc_server)))) + " " + sending_token_symbol)
        retry = 0
        while retry < 3:
            try:
                tx = sending_token_contract.functions.transfer(to_address, token_amount).buildTransaction({'from':self.account_address,'gasPrice': self.w3.toWei(self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 'gwei'), 'nonce': self.w3.eth.getTransactionCount(self.account_address)})
                logger.info("Signing transaction")
                signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
                self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                logger.info("Transaction successfully sent !")

                tx_receipt = self.w3.eth.wait_for_transaction_receipt(transaction_hash=signed_tx.hash, timeout=180,
                                                                    poll_latency=2)  
                logger.info("Transaction mined !")

                token_amount_readable = token_amount * 10 ** (-1 * tokens.decimals(sending_token_address , self.rpc_server))

                logger.info("Successfully transfered %s %s to %s !"%(token_amount_readable,sending_token_symbol,to_address))
                break
            except Exception as e:
                retry += 1
                logger.error("Send Transaction Failed: " + str(e) + " retrying in 5 seconds")
                time.sleep(5)
    
    def SendONE(self, amount, to_address):
        logger.info("Attempting Transfer " + str(amount * (10 ** (-1 * 18))) + " GAS")
        retry = 0
        while retry < 3:
            try:

                tx = {
                    'nonce': self.w3.eth.getTransactionCount(self.account_address),
                    'to': to_address,
                    'value': amount,
                    'gas': 6721900,
                    'gasPrice': self.w3.toWei(self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 'gwei'),
                    'chainId':self.chain_id
                }
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.key)
                self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

                logger.info("Transaction mined !")

                logger.info("Successfully transfered %s %s to %s !"%(amount * (10 ** (-1 * 18)),"GAS",to_address))
                break
            except Exception as e:
                retry += 1
                logger.error("Send Transaction Failed: " + str(e) + " retrying in 5 seconds")
                time.sleep(5)

    def SellItemsToToken(self, token_amount, selling_token_symbol, selling_token_address, to_token_symbol, to_token_address):
        if selling_token_symbol == to_token_symbol:
            return

        logger.info("Attempting Sale " + str(token_amount * (10 ** (-1 * tokens.decimals(selling_token_address , self.rpc_server)))) + " " + selling_token_symbol)
        retry = 0
        while retry < 3:
            try:
                # attempt to sell items 
                tx_receipt = market_place_router.swap_exact_tokens_for_tokens(token_amount, 0,
                                                                            [selling_token_address,  to_token_address],
                                                                            self.account_address,
                                                                            int(time.time() + 60),
                                                                            self.key, self.w3.eth.getTransactionCount(
                        self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout, self.rpc_server, logger,self.market_spending_address)

                token_amount_readable = token_amount * 10 ** (-1 * tokens.decimals(selling_token_address , self.rpc_server))

                logger.info("Successfully sold %s %s to %s !"%(token_amount_readable,selling_token_symbol, to_token_symbol))
                break
            except Exception as e:
                retry += 1
                # Approving Spending limit if transaction fails
                if(str(e) == "execution reverted: TransferHelper: TRANSFER_FROM_FAILED"):
                    logger.info("Transaction Failed, assuming spending limit needs to be set")
                    approve_contract = self.w3.eth.contract(address=selling_token_address,abi=tokens.ABI)
                    self.ApproveSpendingLimit(approve_contract,self.market_spending_address)
                else:
                    logger.error("Sell Transaction Failed: " + str(e) + " retrying in 5 seconds")
                    time.sleep(5)

    def SellItemsToGas(self, token_amount, selling_token_symbol, selling_token_address):
        logger.info("Attempting Sale " + str(token_amount * 10 ** (-1 * tokens.decimals(selling_token_address , self.rpc_server))) + " " + selling_token_symbol)
        retry = 0
        while retry < 3:
            try:
                # attempt to sell items 
                tx_receipt = market_place_router.swap_exact_tokens_for_eth(token_amount, 0,
                                                                            [selling_token_address, self.wrapped_gas],
                                                                            self.account_address,
                                                                            int(time.time() + 60),
                                                                            self.key, self.w3.eth.getTransactionCount(
                        self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout, self.rpc_server, logger,self.market_spending_address)


                token_amount_readable = token_amount * 10 ** (-1 * tokens.decimals(selling_token_address, self.rpc_server))

                logger.info("Successfully sold %s %s to GAS !"%(token_amount_readable,selling_token_symbol))
                break
            except Exception as e:
                retry += 1
                # Approving Spending limit if transaction fails
                if(str(e) == "execution reverted: TransferHelper: TRANSFER_FROM_FAILED"):
                    logger.info("Transaction Failed, assuming spending limit needs to be set")
                    approve_contract = self.w3.eth.contract(address=selling_token_address,abi=tokens.ABI)
                    self.ApproveSpendingLimit(approve_contract,self.market_spending_address)
                else:
                    logger.error("Sell Transaction Failed: " + str(e) + " retrying in 5 seconds")
                    time.sleep(5)
    
    def GetDexPrice(self, token_symbol, token_address):
        logger.info(str(market_place_router.get_amount_in()))
        return

    ##################################################################################################################################
    # Gardening Quest
    def iterateGardeningAutoQuest(self, groups, questing_groups, quest_contract):
        logger.info("Checking gardening")
        self.refreshHeroes()

        # Setting inital veriables
        minimumStamina = 20

        for group in groups:
            try:
                questers_in_group = []
                for quester in questing_groups:
                    for hero_cont in self.heroControllers:
                        if(hero_cont.hero_id == quester):
                            if(hero_cont.quest_address == quest_contract):
                                questers_in_group.append(quester)

                hero_id_group = []
                for controller in group:
                    hero_id_group.append(controller.hero_id)

                heroesInMeditiation = api_functions.returnHeroesMeditation(hero_id_group,self.rpc_server,logger,self.meditation_contract_address)
                
                if(len(heroesInMeditiation) > 0):
                    logger.debug("Hero in group is meditating, skipping for now: %s "%heroesInMeditiation)
                    continue

                for heroController in group:

                    if(heroController.checkup_time > time.time()):
                        continue

                    logger.debug("Checking on Group %s "%group)
                    from_api = api_functions.getHeroInfo(hero_id_group,logger,self.rpc_server,self.hero_contract_address)
                    stamCheck = api_functions.enoughStam(from_api,logger)  # can all heroes in this group run all the attempts?
                    heroesInQuest = api_functions.returnHeroesQuesting(hero_id_group,from_api,logger)  # is none of the heroes in this group currently in a quest?
                    if(stamCheck > 25):
                        stamCheck = 25
                    if stamCheck >= minimumStamina or heroesInQuest.count(heroController.hero_id) > 0:
                        if len(heroesInQuest) == 0:
                            if len(questers_in_group) == 0:
                                logger.info("group: %s ready for questing, attempting quest..." %(hero_id_group))
                                if not self.StartQuestV2(quest_contract, hero_id_group,1,0):
                                    logger.info('Was not able to succesfully start the quest, so skipping this group for now')
                                    heroController.setCheckUpTime(time.time()+60)
                                    continue
                                else:
                                    for hero_id in hero_id_group:
                                        self.questing_gardeners.append(hero_id)
                                        heroesInQuest.append(hero_id)
                                    for heroController in group:
                                        heroController.quest_address = quest_contract
                            else: continue
                        else:
                            logger.info("Already questing, so just picking up time remaining and going from there")

                        quest_info = quest_utils.human_readable_quest(api_functions.getHeroQuest(heroesInQuest[0],self.questV2,logger))

                        try:
                            complete_time = quest_info['startTime'] + 10 * minimumStamina * 60
                            heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                        except:
                            heroController.setCheckUpTime(time.time()+(60)) 
                            continue    
                        
                        if(time.time() > complete_time):
                            retry = 0
                            while True:
                                try:
                                    logger.info("Attempting Quest Completion %s"%(hero_id_group))
                                    tx = self.questV2.complete_quest(heroesInQuest[0], self.key, self.w3.eth.getTransactionCount(self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout)
                                    self.questV2.parse_complete_quest_receipt(tx)['reward']
                                    time.sleep(3)
                                    logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                    for quester in questers_in_group:
                                        self.questing_gardeners.remove(quester)

                                    for heroControl in group:
                                        heroControl.setCheckUpTime(time.time()+(120))  
                                    break
                                except Exception as e:
                                    try:
                                        retry += 1
                                        self.questV2.parse_complete_quest_receipt(tx)     
                                        time.sleep(3)
                                        logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))
                                        for quester in questers_in_group:
                                            self.questing_gardeners.remove(quester)

                                        for heroControl in heroesInQuest:
                                            heroControl.setCheckUpTime(time.time()+(120))  
                                        break
                                    except:
                                        if(retry > 3):
                                            logger.error("Problem with account... remaking now")
                                            self.__init__(self.key)     
                                            return
                                        logger.error("Quest Failed to complete, %s , going to attempt again"%(e))    
                                        time.sleep(2)
                        else:
                            logger.info("Waiting " + str(round((complete_time- time.time()) / 60)) + " minutes to complete quest")
                            for heroController in group:
                                heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                    else:
                        logger.info("Hero %s is not ready to start questing: stamCheck:%s" %(hero_id_group[group.index(heroController)],stamCheck))
                        heroController.setCheckUpTime(time.time()+(20*60*(minimumStamina-stamCheck)))
            except Exception as e:
                 logger.error("Something happened: %s\n Retrying again in 2 minutes." %e)
                 heroController.setCheckUpTime(time.time()+120)

    ##################################################################################################################################
    # Mining Quest
    def iterateMiningAutoQuest(self, groups, questing_groups, quest_contract):
        logger.info("Checking mining")
        self.refreshHeroes()

        # Setting inital veriables
        minimumStamina = 20

        for group in groups:
            try:
                hero_id_group = []
                for controller in group:
                    hero_id_group.append(controller.hero_id)

                heroesInMeditiation = api_functions.returnHeroesMeditation(hero_id_group,self.rpc_server,logger,self.meditation_contract_address)
                
                if(len(heroesInMeditiation) > 0):
                    logger.debug("Hero in group is meditating, skipping for now: %s "%heroesInMeditiation)
                    continue
                for heroController in group:

                    if(heroController.checkup_time > time.time()):
                        continue

                    logger.debug("Checking on Group %s "%group)
                    from_api = api_functions.getHeroInfo(hero_id_group,logger,self.rpc_server,self.hero_contract_address)
                    stamCheck = api_functions.enoughStam(from_api,logger)  # can all heroes in this group run all the attempts?
                    heroesInQuest = api_functions.returnHeroesQuesting(hero_id_group,from_api,logger)  # is none of the heroes in this group currently in a quest?
                    if(stamCheck > 25):
                        stamCheck = 25
                    if stamCheck >= minimumStamina or heroesInQuest.count(heroController.hero_id) > 0:
                        if len(heroesInQuest) == 0:
                            if len(questing_groups) == 0:
                                logger.info("group: %s ready for questing, attempting quest..." %(hero_id_group))
                                if not self.StartQuestV2(quest_contract, hero_id_group,1,0):
                                    logger.info('Was not able to succesfully start the quest, so skipping this group for now')
                                    heroController.setCheckUpTime(time.time()+60)
                                    continue
                                else:
                                    for hero_id in hero_id_group:
                                        self.questing_miners.append(hero_id)
                                        heroesInQuest.append(hero_id)
                            else: continue
                        else:
                            logger.info("Already questing, so just picking up time remaining and going from there")

                        quest_info = quest_utils.human_readable_quest(api_functions.getHeroQuest(heroesInQuest[0],self.questV2,logger))

                        try:
                            complete_time = quest_info['startTime'] + 10 * minimumStamina * 60
                            heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                        except:
                            heroController.setCheckUpTime(time.time()+(60)) 
                            continue    
                        
                        if(time.time() > complete_time):
                            retry = 0
                            while True:
                                try:
                                    logger.info("Attempting Quest Completion %s"%(hero_id_group))
                                    tx = self.questV2.complete_quest(heroesInQuest[0], self.key, self.w3.eth.getTransactionCount(self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout)
                                    self.questV2.parse_complete_quest_receipt(tx)['reward']
                                    time.sleep(3)
                                    logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                    self.questing_miners.clear()

                                    for heroControl in group:
                                        heroControl.setCheckUpTime(time.time()+(120))  
                                    break
                                except Exception as e:
                                    try:
                                        retry += 1
                                        self.questV2.parse_complete_quest_receipt(tx)     
                                        time.sleep(3)
                                        logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                        self.questing_miners.clear()

                                        for heroControl in heroesInQuest:
                                            heroControl.setCheckUpTime(time.time()+(120))  
                                        break
                                    except:
                                        if(retry > 3):
                                            logger.error("Problem with account... remaking now")
                                            self.__init__(self.key)     
                                            return
                                        logger.error("Quest Failed to complete, %s , going to attempt again"%(e))    
                                        time.sleep(2)
                        else:
                            logger.info("Waiting " + str(round((complete_time- time.time()) / 60)) + " minutes to complete quest")
                            for heroController in group:
                                heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                    else:
                        logger.info("Hero %s is not ready to start questing: stamCheck:%s" %(hero_id_group[group.index(heroController)],stamCheck))
                        heroController.setCheckUpTime(time.time()+(20*60*(minimumStamina-stamCheck)))
            except Exception as e:
                 logger.error("Something happened: %s\n Retrying again in 2 minutes." %e)
                 heroController.setCheckUpTime(time.time()+120)

    ##################################################################################################################################
    # Foraging Quest
    def iterateForagingFishingAutoQuest(self, groups, questing_groups, quest_contract):
        logger.info("Checking foraging/Fishing")
        self.refreshHeroes()

        minimumStamina = 20

        for group in groups:
            try:
                hero_id_group = []
                for controller in group:
                    hero_id_group.append(controller.hero_id)

                heroesInMeditiation = api_functions.returnHeroesMeditation(hero_id_group,self.rpc_server,logger,self.meditation_contract_address)
                if(len(heroesInMeditiation) > 0):
                    logger.debug("Hero in group is meditating, skipping for now: %s "%heroesInMeditiation)
                    continue

                for heroController in group:

                    if(heroController.checkup_time > time.time()):
                        continue

                    hero_id_group = []
                    for controller in group:
                        hero_id_group.append(controller.hero_id)

                    logger.debug("Checking on Group %s "%group)
                    from_api = api_functions.getHeroInfo(hero_id_group,logger,self.rpc_server,self.hero_contract_address)
                    
                    lowest_stamina_in_group = from_api["stamina"].min()
                    highest_stamina_in_group = from_api["stamina"].max()

                    abnormal_fix = False
                    if highest_stamina_in_group - lowest_stamina_in_group >= 5:
                        abnormal_fix = True
                        hero_id_group = []
                        heroes_stamina = []
                        for hero_controller in group:
                            heroes_stam = from_api["stamina"][hero_controller.hero_id]
                            if heroes_stam - lowest_stamina_in_group >= 5:
                                hero_id_group.append(hero_controller.hero_id)
                                heroes_stamina.append(heroes_stam)

                        lowest_stamina_in_group = min(heroes_stamina) - lowest_stamina_in_group

                    heroesInQuest = api_functions.returnHeroesQuesting(hero_id_group,from_api,logger)  # is none of the heroes in this group currently in a quest?
                    if(lowest_stamina_in_group > 25): 
                        lowest_stamina_in_group = 25
                    if lowest_stamina_in_group >= minimumStamina or abnormal_fix:
                        if len(heroesInQuest) == 0:
                            if len(questing_groups) == 0:
                                if(abnormal_fix): logger.info("Heroes detected in group with abnormal stamina, attempting to normalize")
                                logger.info("group: %s ready for questing, attempting quest..." %(hero_id_group))    
                                if not self.StartQuestV2(quest_contract, hero_id_group, math.floor(lowest_stamina_in_group/5), 0):
                                    logger.info('Was not able to succesfully start the quest, so skipping this group for now')
                                    heroController.setCheckUpTime(time.time()+60)
                                    continue
                                else:
                                    for hero_id in hero_id_group:
                                        questing_groups.append(hero_id)
                                        heroesInQuest.append(hero_id)
                            else: continue
                        else:
                            logger.info("%s is already questing, so just picking up time remaining and going from there" %(heroesInQuest[0]))
                    else:
                        logger.info("Hero %s is not ready to start questing: stamCheck:%s" %(hero_id_group[group.index(heroController)],lowest_stamina_in_group))
                        heroController.setCheckUpTime(time.time()+(20*60*(minimumStamina-lowest_stamina_in_group)))

                    if heroesInQuest.count(heroController.hero_id) > 0:
                        
                        quest_info = quest_utils.human_readable_quest(api_functions.getHeroQuest(heroesInQuest[0],self.questV2,logger))         

                        try:
                            complete_time = quest_info['completeAtTime']
                            heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                        except:
                            heroController.setCheckUpTime(time.time()+(60)) 
                            continue

                            
                        if(time.time() > complete_time):
                            retry = 0
                            while True:
                                try:
                                    logger.info("Attempting Quest Completion %s"%(hero_id_group))
                                    tx = self.questV2.complete_quest(heroesInQuest[0], self.key, self.w3.eth.getTransactionCount(self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout)
                                    self.questV2.parse_complete_quest_receipt(tx)['reward']
                                    time.sleep(3)
                                    logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                    questing_groups.clear()

                                    for heroControl in group:
                                        heroControl.setCheckUpTime(time.time()+(120))  
                                    break
                                except Exception as e:
                                    try:
                                        retry += 1
                                        self.questV2.parse_complete_quest_receipt(tx)     
                                        time.sleep(3)
                                        logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                        questing_groups.clear()

                                        for heroControl in heroesInQuest:
                                            heroControl.setCheckUpTime(time.time()+(120))  
                                        break
                                    except:
                                        if(retry > 3):
                                            logger.error("Problem with account... remaking now")
                                            self.__init__(self.key)     
                                            return
                                        logger.error("Quest Failed to complete, %s , going to attempt again"%(e))    
                                        time.sleep(2)
                        else:
                            logger.info("Waiting " + str(round((complete_time- time.time()) / 60)) + " minutes to complete quest")
                            for heroController in group:
                                heroController.setCheckUpTime(time.time()+(complete_time-time.time()))   
            except Exception as e:
                logger.error("Something happened: %s\n Retrying again in 2 minutes." % e)
                heroController.setCheckUpTime(time.time()+120)
    
    ##################################################################################################################################
    # Training Quest
    def iterateTrainingAutoQuest(self, group, questing_groups, quest_contract):
        logger.info("Checking Training Quests")
    
        self.refreshHeroes()
        minimumStamina = 20

        for group in group:
            try:
                hero_id_group = []
                for controller in group:
                    hero_id_group.append(controller.hero_id)

                heroesInMeditiation = api_functions.returnHeroesMeditation(hero_id_group,self.rpc_server,logger,self.meditation_contract_address)
                if(len(heroesInMeditiation) > 0):
                    logger.debug("Hero in group is meditating, skipping for now: %s "%heroesInMeditiation)
                    continue

                for heroController in group:
                        
                    if(heroController.checkup_time > time.time()):
                        continue

                    hero_id_group = []
                    for controller in group:
                        hero_id_group.append(controller.hero_id)

                    logger.debug("Checking on Group %s "%group)
                    from_api = api_functions.getHeroInfo(hero_id_group,logger,self.rpc_server,self.hero_contract_address)
                    
                    lowest_stamina_in_group = from_api["stamina"].min()
                    highest_stamina_in_group = from_api["stamina"].max()

                    abnormal_fix = False
                    if highest_stamina_in_group - lowest_stamina_in_group >= 5:
                        abnormal_fix = True
                        logger.info("Heroes detected in group with abnormal stamina, attempting to normalize")
                        hero_id_group = []
                        heroes_stamina = []
                        for hero_controller in group:
                            heroes_stam = from_api["stamina"][hero_controller.hero_id]
                            if heroes_stam - lowest_stamina_in_group >= 5:
                                hero_id_group.append(hero_controller.hero_id)
                                heroes_stamina.append(heroes_stam)

                        lowest_stamina_in_group = min(heroes_stamina) - lowest_stamina_in_group

                    heroesInQuest = api_functions.returnHeroesQuesting(hero_id_group,from_api,logger)  # is none of the heroes in this group currently in a quest?
                    if(lowest_stamina_in_group > 25): 
                        lowest_stamina_in_group = 25
                    if lowest_stamina_in_group >= minimumStamina or abnormal_fix:
                        if len(heroesInQuest) == 0:
                            if len(questing_groups) == 0:
                                if(abnormal_fix): logger.info("Heroes detected in group with abnormal stamina, attempting to normalize")
                                logger.info("group: %s ready for questing, attempting quest..." %(hero_id_group))    
                                if not self.StartQuestV2(quest_contract, hero_id_group, math.floor(lowest_stamina_in_group/5), 1):
                                    logger.info('Was not able to succesfully start the quest, so skipping this group for now')
                                    heroController.setCheckUpTime(time.time()+60)
                                    continue
                                else:
                                    for hero_id in hero_id_group:
                                        questing_groups.append(hero_id)
                                        heroesInQuest.append(hero_id)
                            else: continue
                        else:
                            logger.info("%s is already questing, so just picking up time remaining and going from there" %(heroesInQuest[0]))
                    else:
                        logger.info("Hero %s is not ready to start questing: stamCheck:%s" %(hero_id_group[group.index(heroController)],lowest_stamina_in_group))
                        heroController.setCheckUpTime(time.time()+(20*60*(minimumStamina-lowest_stamina_in_group)))

                    if heroesInQuest.count(heroController.hero_id) > 0:
                        quest_info = quest_utils.human_readable_quest(api_functions.getHeroQuest(heroesInQuest[0],self.questV2,logger))         

                        try:
                            complete_time = quest_info['completeAtTime']
                            heroController.setCheckUpTime(time.time()+(complete_time-time.time()))    
                        except:
                            heroController.setCheckUpTime(time.time()+(60)) 
                            continue

                            
                        if(time.time() > complete_time):
                            retry = 0
                            while True:
                                try:
                                    logger.info("Attempting Quest Completion %s"%(hero_id_group))
                                    tx = self.questV2.complete_quest(heroesInQuest[0], self.key, self.w3.eth.getTransactionCount(self.account_address), self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), self.tx_timeout)
                                    self.questV2.parse_complete_quest_receipt(tx)['reward']

                                    time.sleep(3)
                                    logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                    questing_groups.clear()

                                    for heroControl in group:
                                        heroControl.setCheckUpTime(time.time()+(120))  
                                    break
                                except Exception as e:
                                    try:    
                                        retry += 1
                                        self.questV2.parse_complete_quest_receipt(tx)['reward']    
                                            
                                        time.sleep(3)
                                        logger.info("Quest Completed!, Heroes In Quest %s , Heroes In Group %s"%(heroesInQuest,hero_id_group))

                                        questing_groups.clear()

                                        for heroControl in group:
                                            heroControl.setCheckUpTime(time.time()+(120))  
                                        break
                                    except:   
                                        if(retry > 3):
                                            logger.error("Problem with account... remaking now")
                                            self.__init__(self.key)     
                                            return
                                        logger.error("Quest Failed to complete, %s , going to attempt again"%(e))    
                                        time.sleep(2)
                        else:
                            logger.info("Waiting " + str(round((complete_time- time.time()) / 60)) + " minutes to complete quest")
                            for heroController in group:
                                heroController.setCheckUpTime(time.time()+(complete_time-time.time()))   
            except Exception as e:
                logger.error("Something happened: %s\n Retrying again in 2 minutes." % e)
                heroController.setCheckUpTime(time.time()+120)

    ##################################################################################################################################
    # Sell and/or Transfer Items
    def iterateSellTransferItems(self, item_settings):    
        logger.info("Checking Sell/Transfering")

        # inital variable setup
        to_token_address = self.native_token
        to_token_symbol = tokens.address2symbol(to_token_address,self.tokens)

        minimum_jewel_for_sell = settings_json[int(index)]["OtherAccountSettings"]["MinimumJewelForAutoSell"]

        for item in item_settings:

            if tokens.symbol2address(item["TokenName"],self.tokens) == None and item["TokenName"] != self.gas_name_item: continue

            to_token_from_balance = tokens.balance_of(self.account_address, to_token_address, self.rpc_server)
            to_token_balance = to_token_from_balance * 10 ** (-1 * tokens.decimals(to_token_address , self.rpc_server))

            # Checks if the items setting is set to sell
            if item["AutoSell"] == True and (to_token_balance < minimum_jewel_for_sell or minimum_jewel_for_sell < 0.01):
                try:
                    if(item["TokenName"] != self.gas_name_item):
                        tokenName = item["TokenName"]
                        selling_token_address = tokens.symbol2address(item["TokenName"],self.tokens)

                        selling_token_symbol = tokens.symbol(selling_token_address, self.rpc_server)
                        from_balance = tokens.balance_of(self.account_address, selling_token_address , self.rpc_server)
                        balance = from_balance * 10 ** (-1 * tokens.decimals(selling_token_address , self.rpc_server))
                        logger.info("Checking Sell: "+ tokenName + " Balance: "+str(balance))

                        if ((balance > item["MinQuantityLeft"]) and (balance - item["MinQuantityLeft"] >= item["MinSellAmount"])):

                            amount_to_send = from_balance - (item["MinQuantityLeft"] * (10 ** tokens.decimals(selling_token_address, self.rpc_server)))
                            if(selling_token_address == self.native_token):
                                self.SellItemsToGas(amount_to_send,selling_token_symbol,selling_token_address)
                            else:
                                self.SellItemsToToken(amount_to_send,selling_token_symbol,selling_token_address,to_token_symbol,to_token_address)
                    else:
                        logger.info("Place holder")
                except Exception as e:
                    logger.error("Transaction Failed: %s"%e)
            # Checks if the items setting is set to transfer
            elif(item["AutoTransfer"] != ""):
                try:
                    tokenName = item["TokenName"]
                    to_account_address = item["AutoTransfer"]
                    if(tokenName == self.gas_name_item):
                        from_balance =  self.w3.eth.get_balance(self.account_address)
                        balance = from_balance * 10 ** (-1 * 18)
                    else:
                        sending_token_address = tokens.symbol2address(item["TokenName"],self.tokens)

                        sending_token_symbol = tokens.symbol(sending_token_address, self.rpc_server)

                        from_balance = tokens.balance_of(self.account_address, sending_token_address, self.rpc_server)
                        balance = from_balance * 10 ** (-1 * tokens.decimals(sending_token_address, self.rpc_server))

                    logger.info("Checking Transfer: "+ tokenName + " Balance: "+str(balance))    

                    if ((balance > item["MinQuantityLeft"]) and (balance - item["MinQuantityLeft"] >= item["MinSellAmount"])):
                        if(tokenName == self.gas_name_item):
                            amount_to_send = from_balance - (item["MinQuantityLeft"] * (10 ** 18))
                            self.SendONE(amount_to_send ,to_account_address)
                        else:
                            amount_to_send = from_balance - (item["MinQuantityLeft"] * (10 ** tokens.decimals(sending_token_address, self.rpc_server)))
                            sending_token_contract = self.w3.eth.contract(address=sending_token_address,abi=tokens.ABI)
                            self.SendItems(amount_to_send,sending_token_contract,sending_token_symbol,sending_token_address,to_account_address)

                except Exception as e:
                    logger.error("Transaction Failed: %s"%e)

    def iterateSellNativeForGas(self):
        logger.info("Checking if account is low on gas")
        amount_needed = 1
        try:
            if(self.w3.eth.getBalance(self.account_address)* 10 ** (-1 * 18) < amount_needed):
                native_symbol = tokens.address2symbol(self.native_token,self.tokens)
                native_from_balance = tokens.balance_of(self.account_address, self.native_token, self.rpc_server)
                native_balance = native_from_balance * 10 ** (-1 * tokens.decimals(self.native_token , self.rpc_server))

                amount_to_sell = native_balance
                if native_balance > 1 and native_balance > 0.01:
                    amount_to_sell = 1 * (10 ** tokens.decimals(self.native_token, self.rpc_server))
                elif native_balance < 0.01:
                    amount_to_sell = 0
                else:
                    amount_to_sell = native_from_balance
                
                if(amount_to_sell != 0):     
                    self.SellItemsToGas(amount_to_sell,native_symbol,self.native_token)
        except Exception as e:
            logger.error("Selling Jewel for Gas failed: %s"%e)

    ##################################################################################################################################
    # Leveling
    def iterateLevelingRitual(self):
        logger.info("Checking Leveling")

        try:
            hero_apis = api_functions.getHeroInfo(self.heroes, logger,self.rpc_server,self.hero_contract_address)
            heroes_ready = api_functions.readyForLevelUp(self.heroes, hero_apis, logger)
            heroes_questing = api_functions.returnHeroesQuesting(self.heroes, hero_apis, logger)
            heroes_leveling = list(set(heroes_ready) - set(heroes_questing)) 
                    
            current_meditations = api_functions.getActivateMeditations(self.account_address, self.rpc_server,logger,self.meditation_contract_address)

            if(len(current_meditations) != 0):
                logger.info("Heroes are currently in meditation, finishing them..")
                for current_meditation in current_meditations:
                    
                    if not self.CompleteMeditation(current_meditation[2]):
                        return
                    else:
                        heroes_leveling.remove(current_meditation[2])

            for hero_id in heroes_leveling:
                if self.tavern_heroes.__contains__(hero_id):
                    continue
                
                if settings_json[int(index)]["LevelingBaseSettings"]["DisabledHeroIds"].count(hero_id) > 0:
                    logger.info("Leveling aborted as hero is in disabled hero ids setting " + str(hero_id))
                    continue
    
                levelingSettings = settings_json[int(index)]["LevelingSettings"]
                try:
                    stats = ""
                    enabled = True
                    for classInfo in settings_json[int(index)]["LevelingSettings"]:
                        if(classInfo["Class"] == str(hero_apis["mainClass"][hero_id]).upper()):
                            if(classInfo["Enabled"] == False):
                                logger.info("Meditation not allowed for class: "+str(classInfo["Class"]))
                                enabled = False
                                continue
                            elif(classInfo["ProfessionLevelingEnabled"] == True):
                                stats = GetProfessionStats(hero_id,hero_apis)
                            elif(classInfo["CombatLevelingStatEnabled"] == True):
                                stats = str(levelingSettings[levelingSettings.index(classInfo)]["CombatLevelingStats"])
                    if not enabled:
                        continue
                    logger.info("Meditation Class: %s, Stats: %s" %(str(hero_apis["mainClass"][hero_id]),str(stats)))
                    stats = stats.split(",")
                    if(len(stats) != 3):
                        raise Exception("Stats length not equal to 3 stats")
                    else:
                        stats = [ConvertShortFormStatsToLongForm(stats[0]),ConvertShortFormStatsToLongForm(stats[1]),ConvertShortFormStatsToLongForm(stats[2])]
                        if(stats[0] == "" or stats[1] == "" or stats[2] == ""):
                            raise Exception("could not convert stat to long form, likely incorrect stat name placed in leveling UI")
                except Exception as e:
                    logger.info(traceback.format_exc())
                    logger.info("Getting stats for class failed, trying to redo API: "+str(e))
                    hero_apis = api_functions.getHeroInfo(self.heroes, logger,self.rpc_server,self.hero_contract_address)
                    continue

                self.StartMeditation(hero_id,stats)

            current_meditations = api_functions.getActivateMeditations(self.account_address, self.rpc_server,logger,self.meditation_contract_address)
            if(len(current_meditations) > 0):
                logger.info("waiting 20 seconds then completing all started meditiations: "+str(len(current_meditations)))
                time.sleep(20)
                for current_meditation in current_meditations:
                        if self.CompleteMeditation(current_meditation[2]):
                            heroes_leveling.remove(current_meditation[2])
        except Exception as e:
            logger.error("Leveling Iteration: %s"%e)

    ##################################################################################################################################
    # Tavern Selling
    def iterateTavernSelling(self):
        zero_address = "0x0000000000000000000000000000000000000000"
        try:
            leveling_heroes = []
            for key,value in self.tavern_heroes.items():
                leveling_heroes.append(int(key))
            hero_api = api_functions.getHeroInfo(leveling_heroes, logger,self.rpc_server,self.hero_contract_address)
        except Exception as e:
            logger.info("Hero not on this blockchain, or ID is not set correctly, please double check ID if the hero is not listed, " + str(e))
            return 

        for key,value in self.tavern_heroes.items():
            try:
                hero_id = int(key)
                hero_stamina = hero_api['stamina'][hero_id]
                try:
                    is_on_action = Auction.is_on_auction(self.auction_address, hero_id, self.rpc_server)
                except:
                    return 
                    
                if(hero_stamina >= 19 and is_on_action):
                    retry = 0
                    while retry < 3:
                        try:
                            Auction.cancel_auction(self.auction_address, hero_id, self.key, self.w3.eth.getTransactionCount(self.account_address),self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 30,self.rpc_server)
                            logger.info("Tavern Listing Removed For Questing: %s"%hero_id)
                            break
                        except Exception as e:
                            logger.error("Tavern Listing Failed: %s"%e)
                            retry += 1

                elif hero_stamina < 19 and is_on_action == False:
                    if(self.heroes.count(hero_id) == 0): continue
                    retry = 0
                    while retry < 3:
                        try:
                            Auction.create_auction(self.auction_address,hero_id, int(value*(10**18)),int(value*(10**18)),60,zero_address,self.key,self.w3.eth.getTransactionCount(self.account_address),self.gas_price_gwei+(retry*(self.gas_price_gwei/10)), 30,self.rpc_server)
                            logger.info("Tavern Listing Succeeded ! :  %s"%hero_id)
                            break
                        except Exception as e:
                            logger.error("Tavern Listing Failed: %s"%e)
                            if(str(e) == "execution reverted: ERC721: transfer caller is not owner nor approved"):
                                contract = self.w3.eth.contract(address=self.hero_contract_address,abi=MarketAbi.ABI)
                                self.SetApprovalForAll(contract,self.auction_address)
                            retry += 1
                    if retry >= 3:
                        raise Exception("Failed to crate auction")
            except Exception as e:
                logger.error("Hero "+ str(key) + " Failed to list, error : " + str(e))

##################################################################################################################################
 # other Functions
def GetProfessionStats(hero_id, hero_apis):
    if(hero_apis["profession"][hero_id] == "gardening"):
        return "LCK,WIS,VIT"
    elif(hero_apis["profession"][hero_id] == "mining"):
        return "LCK,STR,END"
    elif(hero_apis["profession"][hero_id] == "foraging"):
        return "LCK,DEX,INT"
    elif(hero_apis["profession"][hero_id] == "fishing"):
        return "VIT,LCK,AGI"
    return ""
        
def ConvertShortFormStatsToLongForm(short_form):
    if(short_form == "STR"): return "strength"
    elif(short_form == "END"): return "endurance"
    elif(short_form == "VIT"): return "vitality"
    elif(short_form == "WIS"): return "wisdom"
    elif(short_form == "INT"): return "intelligence"
    elif(short_form == "DEX"): return "dexterity"
    elif(short_form == "AGI"): return "agility"
    elif(short_form == "LCK"): return "luck"
    else: return ""



##################################################################################################################################
# main code
if __name__ == "__main__":
    #Settings and Setup
    logger = logger_functions.setLoggerConfig()
    warnings.filterwarnings('ignore')

    # get settings for account
    settings_json = json.loads(open("settings.json").read())
    key = sys.argv[1]
    index = sys.argv[2]

    accounts = []
    
    logger.info("Setting up account for CV...")
    account = accountQuestManager(key)
    logger.info("Successfully setup account for CV!")

    while True:
        try:
            if settings_json[int(index)]["OtherAccountSettings"]["ConvertForGas"] == True:
                account.iterateSellNativeForGas()

            #Professions
            if settings_json[int(index)]["GardeningSettings"]["Enabled"] == True:
                gardener_index = 0
                for address in account.gardening_contract_address:
                    amount = 0
                    these_gardeners = []
                    while amount < 3:
                        if(gardener_index < len(account.gardening_groups)):
                            these_gardeners.append(account.gardening_groups[gardener_index])
                        gardener_index += 1
                        amount += 1

                    account.iterateGardeningAutoQuest(these_gardeners,account.questing_gardeners, address)

            
            if settings_json[int(index)]["MiningSettings"]["Enabled"] == True:
                account.iterateMiningAutoQuest(account.mining_groups,account.questing_miners, account.mining_contract_address)

            if settings_json[int(index)]["ForagingSettings"]["Enabled"] == True:                                            
                account.iterateForagingFishingAutoQuest(account.foraging_groups,account.questing_foragers, account.foraging_contract_address)
            if settings_json[int(index)]["FishingSettings"]["Enabled"] == True:
                account.iterateForagingFishingAutoQuest(account.fishing_groups,account.questing_fishers, account.fishing_contract_address)

            #Training Quests

            if settings_json[int(index)]["TrainingSettings"]["Enabled"] == True:
                account.iterateTrainingAutoQuest(account.arm_wrestling_groups,account.questing_arm_wrestling, account.str_contract_address)
                account.iterateTrainingAutoQuest(account.game_of_ball_groups,account.questing_game_of_ball, account.agi_contract_address)
                account.iterateTrainingAutoQuest(account.dancing_groups,account.questing_dancing, account.end_contract_address)
                account.iterateTrainingAutoQuest(account.puzzle_solving_groups,account.questing_puzzle_solving, account.wis_contract_address)
                account.iterateTrainingAutoQuest(account.darts_groups,account.questing_darts, account.dex_contract_address)
                account.iterateTrainingAutoQuest(account.helping_the_farm_groups,account.questing_helping_the_farm, account.vit_contract_address)
                account.iterateTrainingAutoQuest(account.alchemist_assistance_groups,account.questing_alchemist_assistance, account.int_contract_address)
                account.iterateTrainingAutoQuest(account.card_game_groups,account.questing_card_game, account.lck_contract_address)

            #Leveling Management
            if settings_json[int(index)]["LevelingBaseSettings"]["Enabled"] == True:
                account.iterateLevelingRitual()

            #Account Management
            
            account.iterateSellTransferItems(settings_json[int(index)]["Inventory"])
            
            #Tavern Management
            if settings_json[int(index)]["TavernSettings"]["Enabled"] == True:
                account.iterateTavernSelling()
                
        except Exception as e:
            logger.error("Main execution failed, restarting : " + str(e))
            raise Exception("Failed")
    





    



        

        

