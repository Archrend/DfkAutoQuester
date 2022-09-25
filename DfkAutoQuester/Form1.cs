using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Newtonsoft.Json;
using System.IO;
using System.Diagnostics;
using System.Security.Cryptography;

namespace DfkAutoQuester
{
    public partial class Form1 : Form
    {
        #region Form Variables
        public List<Account> currentAccounts { get; set; }
        private List<Process> autoQuesters;
        private List<string> autoQuesterConsoleLogs;
        public Account selectedAccount;
        public string settingsLocation = AppDomain.CurrentDomain.BaseDirectory + @"settings.json";
        public string exeLocation = AppDomain.CurrentDomain.BaseDirectory + @"AutoQuester\dist\auto_quester\auto_quester";
        public Account.Item selectedItem;
        public Account.ClassLevelingSettings selectedClassType;
        public bool running = false;
        delegate void SetTextCallback(string text);
        #endregion
        #region Classes
        public class Account
        {
            public class Item
            {
                public string TokenName { get; set; } = "";
                public bool AutoSell { get; set; } = false;
                public string AutoTransfer { get; set; } = "";
                public int MinQuantityLeft { get; set; } = 0;
                public int MinSellAmount { get; set; } = 1;
            }

            public class ClassLevelingSettings
            {
                public bool Enabled { get; set; } = true;
                public string Class { get; set; } = "";
                public bool ProfessionLevelingEnabled { get; set; } = true;
                public bool CombatLevelingStatEnabled { get; set; } = false;
                public string CombatLevelingStats { get; set; } = "";
            }

            public class GardeningProfessionSettings
            {
                public bool Enabled { get; set; } = true;
                public bool ConvertGardeningJewelToGas { get; set; } = false;
                public Dictionary<string, List<long>> PoolHeroIds { get; set; } = new Dictionary<string, List<long>>();
            }
            public class MiningProfessionSettings
            {
                public bool Enabled { get; set; } = true;
                public bool JewelEnabled { get; set; } = true;

                public bool LeaderBeforeTQ { get; set; } = false;
            }
            public class ForagingProfessionSettings
            {
                public bool Enabled { get; set; } = true;
            }
            public class FishingProfessionSettings
            {
                public bool Enabled { get; set; } = true;
            }
            public class LevelingOverallSettings
            {
                public bool Enabled { get; set; } = false;
                public List<long> DisabledHeroIds { get; set; } = new List<long>();
            }
            public class TrainingQuestSettings
            {
                public bool Enabled { get; set; } = true;
                public int MinGardeningProfSkill { get; set; } = 10;
                public int MinMiningProfSkill { get; set; } = 10;
                public int MinForagingProfSkill { get; set; } = 10;
                public int MinFishingProfSkill { get; set; } = 10;

                public int MinStatRequirement { get; set; } = 15;
            }

            public class TavernSellingSettings
            {
                public bool Enabled { get; set; } = false;
                public Dictionary<long, long> SellingHeroIds { get; set; } = new Dictionary<long, long>();
            }

            public class OtherSettings
            {
                public bool ConvertForGas { get; set; } = false;
                public float MinimumJewelForAutoSell { get; set; } = 0;
                public string RPC { get; set; } = "https://rpc.ankr.com/harmony";
                public int GWEI { get; set; } = 35;
                public float DFKGWEI { get; set; } = 1.5f;
            }

            public string AccountName { get; set; } = "Account Name";
            public string PrivateKey { get; set; } = "";

            public GardeningProfessionSettings GardeningSettings { get; set; } = new GardeningProfessionSettings();
            public MiningProfessionSettings MiningSettings { get; set; } = new MiningProfessionSettings();
            public ForagingProfessionSettings ForagingSettings { get; set; } = new ForagingProfessionSettings();
            public FishingProfessionSettings FishingSettings { get; set; } = new FishingProfessionSettings();
            public TrainingQuestSettings TrainingSettings { get; set; } = new TrainingQuestSettings();
            public LevelingOverallSettings LevelingBaseSettings { get; set; } = new LevelingOverallSettings();
            public TavernSellingSettings TavernSettings { get; set; } = new TavernSellingSettings();

            public OtherSettings OtherAccountSettings { get; set; } = new OtherSettings();
            public List<Item> Inventory { get; set; } = new List<Item>();
            public List<Item> InventoryCV { get; set; } = new List<Item>();
            public List<ClassLevelingSettings> LevelingSettings { get; set; } = new List<ClassLevelingSettings>();

    }
        #endregion
        #region Buttons
        private void StamPotEnabled_CheckedChanged(object sender, EventArgs e)
        {

        }
        // Buttons
        private void QuestingButton_Click(object sender, EventArgs e)
        {
            if (currentAccounts != null && currentAccounts.Count > 0)
            {
                if (autoQuesters == null || autoQuesters[0].HasExited)
                {
                    string password = PasswordTextBox.Text;
                    if (password.Length == 0) return;

                    foreach(Account account in currentAccounts)
                    {
                        // Not encrypted
                        if(account.PrivateKey.Length == 64)
                        {
                            var data = Encoding.Unicode.GetBytes(account.PrivateKey);
                            byte[] encrypted = ProtectedData.Protect(data, Encoding.Unicode.GetBytes(password), DataProtectionScope.LocalMachine);
                            account.PrivateKey = Convert.ToBase64String(encrypted);
                        }
                    }

                    if (RunCmds())
                    {
                        QuestingButton.Text = "Stop Questing";
                        running = true;
                        if (selectedAccount != null)
                        {
                            SetConsoleText(autoQuesterConsoleLogs[currentAccounts.IndexOf(selectedAccount)]);
                        }
                    }
                }
                else
                {
                    QuestingButton.Text = "Start Questing";
                    foreach(Process autoQuester in autoQuesters)
                    {
                        autoQuester.Kill();
                    }
                    autoQuesters = null;
                    autoQuesterConsoleLogs = null;
                    running = false;
                }
            }
        }
        private void ItemButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                foreach (Account.Item item in selectedAccount.Inventory)
                {
                    if (item.TokenName == ((Button)sender).Name)
                    {
                        SelectItem(null);
                        SelectItem(item);
                    }
                }
            }
        }

        private void ClassTypeButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                foreach (Account.ClassLevelingSettings levelingSetting in selectedAccount.LevelingSettings)
                {
                    if (levelingSetting.Class == ((Button)sender).Name)
                    {
                        SelectClassType(levelingSetting);
                    }
                }
            }
        }

        private void AddKeyButton_Click(object sender, EventArgs e)
        {
            // Ensure no duplicates or invalid entrys
            if (AddKeyTextBox.Text.Length != 64) { return; }
            if (AddAccountNameTextBox.Text == string.Empty) { return; }
            if (PasswordTextBox.Text == string.Empty) { return; }

            foreach (Account account in currentAccounts)
            {
                if (account.PrivateKey == AddKeyTextBox.Text)
                {
                    return;
                }
            }

            // create new account
            CreateNewAccount(AddAccountNameTextBox.Text, AddKeyTextBox.Text, PasswordTextBox.Text);
            AddKeyTextBox.Text = "";
            AddAccountNameTextBox.Text = "";
        }

        private void RemoveKeyButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                currentAccounts.Remove(selectedAccount);
                AccountListBox.SelectedIndex = -1;
                RefreshAccountBox();
            }
        }
        private void RemoveHeroIdButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    if (DisableHeroLevelingListBox.SelectedIndex != -1)
                    {
                        long heroId = (long)DisableHeroLevelingListBox.SelectedItem;
                        if (selectedAccount.LevelingBaseSettings.DisabledHeroIds.Contains(heroId))
                        {
                            selectedAccount.LevelingBaseSettings.DisabledHeroIds.Remove(heroId);
                            RefreshDisableLevelingHeroesListBox();
                        }
                    }
                }
                catch { }
            }
        }
        private void AddHeroIdButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    long heroId = long.Parse(DisableLevelingHeroIdTextBox.Text);
                    if (!selectedAccount.LevelingBaseSettings.DisabledHeroIds.Contains(heroId))
                    {
                        selectedAccount.LevelingBaseSettings.DisabledHeroIds.Add(heroId);
                        RefreshDisableLevelingHeroesListBox();
                    }
                }
                catch { }
            }
        }
        private void AddHeroSellingButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    long heroId = long.Parse(SellingIDTextBox.Text);
                    long heroPrice = long.Parse(SellingPriceTextBox.Text);
                    if (selectedAccount.TavernSettings.SellingHeroIds.ContainsKey(heroId))
                    {
                        selectedAccount.TavernSettings.SellingHeroIds[heroId] = heroPrice;
                        RefreshTavernSellingBox();
                    }
                    else
                    {
                        selectedAccount.TavernSettings.SellingHeroIds.Add(heroId, heroPrice);
                        RefreshTavernSellingBox();
                    }
                }
                catch { }
            }
        }

        private void RemoveHeroSellingButton_Click(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    if (AddHeroSellingListBox.SelectedIndex != -1)
                    {
                        string[] heroStringList = AddHeroSellingListBox.SelectedItem.ToString().Split(' ');

                        long heroId = long.Parse(heroStringList[0]);
                        if (selectedAccount.TavernSettings.SellingHeroIds.ContainsKey(heroId))
                        {
                            selectedAccount.TavernSettings.SellingHeroIds.Remove(heroId);
                            RefreshTavernSellingBox();
                        }
                    }
                }
                catch { }
            }
        }

 

        #endregion
        #region CheckBoxes

        private void ConvertForGasCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if(selectedAccount != null)
            {
                selectedAccount.OtherAccountSettings.ConvertForGas = ConvertForGasCheckBox.Checked;
            }
            else
            {
                ConvertForGasCheckBox.Checked = false;
            }
        }
        private void ProfessionLevelingCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if(selectedClassType != null)
            {
                selectedClassType.ProfessionLevelingEnabled = ProfessionLevelingCheckBox.Checked;
                selectedClassType.CombatLevelingStatEnabled = !ProfessionLevelingCheckBox.Checked;
                CombatLevelingCheckBox.Checked = !ProfessionLevelingCheckBox.Checked;
            }
            else
            {
                ProfessionLevelingCheckBox.Checked = false;
            }
        }

        private void LevelingEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedClassType != null)
            {
                selectedClassType.Enabled = LevelingEnabledCheckBox.Checked;
            }
            else
            {
                LevelingEnabledCheckBox.Checked = false;
            }
        }

        private void CombatLevelingCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedClassType != null)
            {
                selectedClassType.CombatLevelingStatEnabled = CombatLevelingCheckBox.Checked;
                selectedClassType.ProfessionLevelingEnabled = !CombatLevelingCheckBox.Checked;
                ProfessionLevelingCheckBox.Checked = !CombatLevelingCheckBox.Checked;
            }
            else
            {
                CombatLevelingCheckBox.Checked = false;
            }
        }

        private void TrainingEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.TrainingSettings.Enabled = TrainingEnabledCheckBox.Checked;
            }
            else
            {
                TrainingEnabledCheckBox.Checked = false;
            }
        }
        private void AutoSellCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedItem != null)
            {
                selectedItem.AutoSell = AutoSellCheckBox.Checked;
                selectedItem.AutoTransfer = string.Empty;
                AutoTransferTextBox.Text = string.Empty;
            }
            else
            {
                AutoSellCheckBox.Checked = false;
            }
        }

        private void GardeningConvertJewelCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if(selectedAccount != null)
            {
                selectedAccount.GardeningSettings.ConvertGardeningJewelToGas = GardeningConvertJewelCheckBox.Checked;
            }
            else
            {
                GardeningConvertJewelCheckBox.Checked = false;
            }
        }
        private void GardeningEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.GardeningSettings.Enabled = GardeningEnabledCheckBox.Checked;
            }
            else
            {
                GardeningEnabledCheckBox.Checked = false;
            }
        }

        private void MiningEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.MiningSettings.Enabled = MiningEnabledCheckBox.Checked;
            }
            else
            {
                MiningEnabledCheckBox.Checked = false;
            }
        }

        private void FishingEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.FishingSettings.Enabled = FishingEnabledCheckBox.Checked;
            }
            else
            {
                FishingEnabledCheckBox.Checked = false;
            }
        }
        private void TavernEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.TavernSettings.Enabled = TavernEnabledCheckBox.Checked;
            }
            else
            {
                TavernEnabledCheckBox.Checked = false;
            }
        }
        private void ForagingEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.ForagingSettings.Enabled = ForagingEnabledCheckBox.Checked;
            }
            else
            {
                ForagingEnabledCheckBox.Checked = false;
            }
        }
        private void LevelingSettingEnabledCheckBox_CheckedChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                selectedAccount.LevelingBaseSettings.Enabled = LevelingSettingEnabledCheckBox.Checked;
            }
            else
            {
                LevelingSettingEnabledCheckBox.Checked = false;
            }
        }
        #endregion
        #region TextBoxes
        private void MinStatRequirementTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.TrainingSettings.MinStatRequirement = int.Parse(MinStatRequirementTextBox.Text);
                }
                catch
                {
                    MinStatRequirementTextBox.Text = "15";
                    selectedAccount.TrainingSettings.MinStatRequirement = 15;
                }
            }
        }
        private void GasPriceTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.OtherAccountSettings.GWEI = int.Parse(GasPriceTextBox.Text);
                }
                catch
                {
                    GasPriceTextBox.Text = "35";
                    selectedAccount.OtherAccountSettings.GWEI = 35;
                }
            }
        }
        private void DFKGasPriceTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.OtherAccountSettings.DFKGWEI = float.Parse(DFKGasPriceTextBox.Text);
                }
                catch
                {
                    GasPriceTextBox.Text = "1.5";
                    selectedAccount.OtherAccountSettings.DFKGWEI = 35;
                }
            }
        }

        private void AutoSellWhenTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.OtherAccountSettings.MinimumJewelForAutoSell = float.Parse(AutoSellWhenTextBox.Text);
                }
                catch
                {
                    AutoSellWhenTextBox.Text = "";
                    selectedAccount.OtherAccountSettings.MinimumJewelForAutoSell = 0;
                }
            }
        }
        private void RPCTextBox_TextChanged(object sender, EventArgs e)
        {
            if(selectedAccount != null)
            {
                try
                {
                    selectedAccount.OtherAccountSettings.RPC = RpcTextBox.Text;
                }
                catch
                {
                    RpcTextBox.Text = "https://rpc.ankr.com/harmony";
                    selectedAccount.OtherAccountSettings.RPC = "https://rpc.ankr.com/harmony";
                }
            }
        }
        private void MinGardeningProfSkillTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.TrainingSettings.MinGardeningProfSkill = int.Parse(MinGardeningSkillTextBox.Text);
                }
                catch
                {
                    selectedAccount.TrainingSettings.MinGardeningProfSkill = 10;
                }
            }
        }
        private void MinMiningSkillTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.TrainingSettings.MinMiningProfSkill= int.Parse(MinMiningSkillTextBox.Text);
                }
                catch
                {
                    selectedAccount.TrainingSettings.MinMiningProfSkill = 10;
                }
            }
        }

        private void MinFishingSkillTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.TrainingSettings.MinFishingProfSkill = int.Parse(MinFishingSkillTextBox.Text);
                }
                catch
                {
                    selectedAccount.TrainingSettings.MinFishingProfSkill = 10;
                }
            }
        }

        private void MinForagingSkillTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedAccount != null)
            {
                try
                {
                    selectedAccount.TrainingSettings.MinForagingProfSkill = int.Parse(MinForagingSkillTextBox.Text);
                }
                catch
                {
                    selectedAccount.TrainingSettings.MinForagingProfSkill = 10;
                }
            }
        }

        private void ConsoleTextBox_TextChanged(object sender, EventArgs e)
        {
            ConsoleTextBox.SelectionStart = ConsoleTextBox.Text.Length;
            ConsoleTextBox.ScrollToCaret();
        }

        private void MinimumLeftInWalletTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedItem != null)
            {
                selectedItem.MinQuantityLeft = int.Parse(MinimumLeftInWalletTextBox.Text);
            }
            else
            {
                MinimumLeftInWalletTextBox.Text = string.Empty;
            }
        }

        private void MinimumQuantityUntilSellSendTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedItem != null)
            {
                selectedItem.MinSellAmount = int.Parse(MinimumQuantityUntilSellSendTextBox.Text);
            }
            else
            {
                MinimumQuantityUntilSellSendTextBox.Text = string.Empty;
            }
        }

        private void AutoTransferTextBox_TextChanged(object sender, EventArgs e)
        {
            if (selectedItem != null)
            {
                if (AutoTransferTextBox.Text != string.Empty)
                {
                    selectedItem.AutoSell = false;
                    AutoSellCheckBox.Checked = false;
                }
                selectedItem.AutoTransfer = AutoTransferTextBox.Text;
            }
            else
            {
                AutoTransferTextBox.Text = string.Empty;
            }
        }
        #endregion
        #region Form Functions
        public Form1()
        {
            InitializeComponent();

            try
            {
                LoadJson();
            }
            catch
            {
                File.Delete(settingsLocation);
            }

            if(currentAccounts == null)
            {
                currentAccounts = new List<Account>();
            }
            RefreshAccountBox();

            foreach (Account account in currentAccounts)
            {
                SelectAccount(account);
                SelectAccount(null);
            }
        }
        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveJson();
            try
            {
                if (autoQuesters != null)
                {
                    foreach (Process autoQuester in autoQuesters)
                    {
                        try
                        {
                            autoQuester.Kill();
                        }
                        catch { }
                    }
                }
            }
            catch { }
        }
        #endregion
        #region ListBox Functions
        private void AccountListBox_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (AccountListBox.SelectedIndex != -1)
            {
                foreach (Account thisAccount in currentAccounts)
                {
                    if (thisAccount.AccountName == AccountListBox.SelectedItem.ToString())
                    {
                        SelectAccount(thisAccount);
                    }
                }
            }
            else
            {
                SelectAccount(null);
            }
        }
        #endregion
        #region Timer Functions
        private void CheckTimer(object sender, EventArgs e)
        {
            if (running == true)
            {
                bool restart = false;
                foreach (Process p in autoQuesters)
                {
                    if (p.HasExited)
                    {
                        restart = true;
                        running = false;
                    }
                }
                if (restart)
                {
                    foreach (Process p in autoQuesters)
                    {
                        p.Kill();
                    }
                    autoQuesters = null;
                    QuestingButton_Click(null, null);
                }
            }
        }
        #endregion
        #region Internal Functions

        private void SaveJson()
        {
            string accountJson = JsonConvert.SerializeObject(currentAccounts, Formatting.Indented);
            File.WriteAllText(settingsLocation, accountJson);
        }

        private void LoadJson()
        {
            currentAccounts = JsonConvert.DeserializeObject<List<Account>>(File.ReadAllText(settingsLocation));
        }

        private void LoadFormVariables()
        {
            SelectItem(null);
            SelectClassType(null);

            GardeningEnabledCheckBox.Checked = selectedAccount.GardeningSettings.Enabled;
            MiningEnabledCheckBox.Checked = selectedAccount.MiningSettings.Enabled;
            ForagingEnabledCheckBox.Checked = selectedAccount.ForagingSettings.Enabled;
            LevelingSettingEnabledCheckBox.Checked = selectedAccount.LevelingBaseSettings.Enabled;
            FishingEnabledCheckBox.Checked = selectedAccount.FishingSettings.Enabled;
            TrainingEnabledCheckBox.Checked = selectedAccount.TrainingSettings.Enabled;
            MinGardeningSkillTextBox.Text = selectedAccount.TrainingSettings.MinGardeningProfSkill.ToString();
            MinMiningSkillTextBox.Text = selectedAccount.TrainingSettings.MinMiningProfSkill.ToString();
            MinFishingSkillTextBox.Text = selectedAccount.TrainingSettings.MinFishingProfSkill.ToString();
            MinForagingSkillTextBox.Text = selectedAccount.TrainingSettings.MinForagingProfSkill.ToString();
            MinStatRequirementTextBox.Text = selectedAccount.TrainingSettings.MinStatRequirement.ToString();
            ConvertForGasCheckBox.Checked = selectedAccount.OtherAccountSettings.ConvertForGas;
            RpcTextBox.Text = selectedAccount.OtherAccountSettings.RPC;
            GasPriceTextBox.Text = selectedAccount.OtherAccountSettings.GWEI.ToString();
            DFKGasPriceTextBox.Text = selectedAccount.OtherAccountSettings.DFKGWEI.ToString();
            TavernEnabledCheckBox.Checked = selectedAccount.TavernSettings.Enabled;

            if (selectedAccount.OtherAccountSettings.MinimumJewelForAutoSell != 0)
            {
                AutoSellWhenTextBox.Text = selectedAccount.OtherAccountSettings.MinimumJewelForAutoSell.ToString();
            }
            else
            {
                AutoSellWhenTextBox.Text = "";
            }
            RefreshDisableLevelingHeroesListBox();
            RefreshTavernSellingBox();

            List<Account.Item> inventoryCheck = CreateItemList();
            for (int x = 0; x < inventoryCheck.Count(); x++)
            {
                if (selectedAccount.Inventory.Count-1 < x)
                {
                    selectedAccount.Inventory.Add(inventoryCheck[x]);
                }
                else
                {
                    if (selectedAccount.Inventory[x].TokenName != inventoryCheck[x].TokenName)
                    {
                        selectedAccount.Inventory[x] = inventoryCheck[x];
                    }
                }
            }
            List<Account.ClassLevelingSettings> classLevelingCheck = CreateClassLevelingList();
            for (int x = 0; x < classLevelingCheck.Count(); x++)
            {
                if (selectedAccount.LevelingSettings.Count - 1 < x)
                {
                    selectedAccount.LevelingSettings.Add(classLevelingCheck[x]);
                }
                else
                {
                    if (selectedAccount.LevelingSettings[x].Class != classLevelingCheck[x].Class)
                    {
                        selectedAccount.LevelingSettings[x] = classLevelingCheck[x];
                    }
                }
            }

            if (autoQuesterConsoleLogs != null)
            {
                SetConsoleText(autoQuesterConsoleLogs[currentAccounts.IndexOf(selectedAccount)]);
            }
        }

        private void ResetFormVariables()
        {
            SelectItem(null);
            SelectClassType(null);

            GardeningEnabledCheckBox.Checked = true;
            MiningEnabledCheckBox.Checked = true;
            ForagingEnabledCheckBox.Checked = true;
            LevelingSettingEnabledCheckBox.Checked = false;
            FishingEnabledCheckBox.Checked = true;
            TrainingEnabledCheckBox.Checked = true;

            MinGardeningSkillTextBox.Text = "10";
            MinMiningSkillTextBox.Text = "10";
            MinFishingSkillTextBox.Text = "10";
            MinForagingSkillTextBox.Text = "10";
            MinStatRequirementTextBox.Text = "15";

            ConvertForGasCheckBox.Checked = false;
            AutoSellWhenTextBox.Text = "";
            RpcTextBox.Text = "https://rpc.ankr.com/harmony";
            GasPriceTextBox.Text = "35";
            DFKGasPriceTextBox.Text = "1.5";
            TavernEnabledCheckBox.Checked = false;

            RefreshDisableLevelingHeroesListBox();
            RefreshTavernSellingBox();

            SetConsoleText("");
        }

        private void SelectAccount(Account account)
        {
            selectedAccount = account;
            if (selectedAccount == null)
            {
                ResetFormVariables();
            }
            else
            {
                LoadFormVariables();
            }
        }

        private void SelectItem(Account.Item item)
        {
            selectedItem = item;

            if (item == null)
            {
                CurrentItemLabel.Text = "Current Item";
                AutoSellCheckBox.Checked = false;
                AutoTransferTextBox.Text = "";
                MinimumLeftInWalletTextBox.Text = "";
                MinimumQuantityUntilSellSendTextBox.Text = "";
            }
            else
            {
                CurrentItemLabel.Text = selectedItem.TokenName;
                AutoSellCheckBox.Checked = selectedItem.AutoSell;
                AutoTransferTextBox.Text = selectedItem.AutoTransfer;
                MinimumLeftInWalletTextBox.Text = selectedItem.MinQuantityLeft.ToString();
                MinimumQuantityUntilSellSendTextBox.Text = selectedItem.MinSellAmount.ToString();
            }
        }

        private void SelectClassType(Account.ClassLevelingSettings classTypeLeveling)
        {
            selectedClassType = classTypeLeveling;

            if (classTypeLeveling == null)
            {
                CurrentClassTypeLabel.Text = "Current Leveling Type";
                LevelingEnabledCheckBox.Checked = false;
                ProfessionLevelingCheckBox.Checked = false;
                CombatLevelingCheckBox.Checked = false;
                CombatLevelingTextBox.Text = "";
            }
            else
            {
                CurrentClassTypeLabel.Text = classTypeLeveling.Class;
                LevelingEnabledCheckBox.Checked = classTypeLeveling.Enabled;
                ProfessionLevelingCheckBox.Checked = classTypeLeveling.ProfessionLevelingEnabled;
                CombatLevelingCheckBox.Checked = classTypeLeveling.CombatLevelingStatEnabled;
                CombatLevelingTextBox.Text = classTypeLeveling.CombatLevelingStats;
            }
        }

        private bool RunCmds()
        {
            SaveJson();

            autoQuesters = new List<Process>();
            autoQuesterConsoleLogs = new List<string>();

            foreach (Account account in currentAccounts)
            {
                string key = "";
                try
                {
                    byte[] decrypted = ProtectedData.Unprotect(Convert.FromBase64String(account.PrivateKey), Encoding.Unicode.GetBytes(PasswordTextBox.Text), DataProtectionScope.LocalMachine);
                    key = Encoding.Unicode.GetString(decrypted);
                }
                catch
                {
                    autoQuesters = null;
                    autoQuesterConsoleLogs = null;
                    MessageBox.Show("Invalid Password");
                    return false;
                }

                Process p = new Process();

                p.StartInfo = new ProcessStartInfo(exeLocation, key + " " +currentAccounts.IndexOf(account).ToString())
                {
                    RedirectStandardOutput = true,
                    RedirectStandardInput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                autoQuesterConsoleLogs.Add("");

                try
                {
                    p.OutputDataReceived += (s, e) =>
                    {
                        if (!p.HasExited)
                        {
                            autoQuesterConsoleLogs[currentAccounts.IndexOf(account)] += e.Data + "\n";
                            if (selectedAccount == account)
                            {
                                SetConsoleText(autoQuesterConsoleLogs[currentAccounts.IndexOf(selectedAccount)]);
                            }
                        }
                    };
                }
                catch { }

                p.Start();
                p.BeginOutputReadLine();
                autoQuesters.Add(p);
            }
            return true;
        }
        private void RefreshAccountBox()
        {
            AccountListBox.Items.Clear();
            foreach (Account thisAccount in currentAccounts)
            {
                AccountListBox.Items.Add(thisAccount.AccountName);
            }
        }

        private void RefreshTavernSellingBox()
        {
            AddHeroSellingListBox.Items.Clear();
            if (selectedAccount != null)
            {
                foreach (KeyValuePair<long, long> kv in selectedAccount.TavernSettings.SellingHeroIds)
                {
                    AddHeroSellingListBox.Items.Add(kv.Key.ToString() + " : "+kv.Value.ToString()+"J/C");
                }
            }
        }
        private void RefreshDisableLevelingHeroesListBox()
        {
            DisableHeroLevelingListBox.Items.Clear();
            if (selectedAccount != null)
            {
                foreach (long hero_id in selectedAccount.LevelingBaseSettings.DisabledHeroIds)
                {
                    DisableHeroLevelingListBox.Items.Add(hero_id);
                }
            }
        }
        private void SetConsoleText(string text)
        {
            if (ConsoleTextBox.InvokeRequired)
            {
                SetTextCallback d = new SetTextCallback(SetConsoleText);
                Invoke(d, new object[] { text });
            }
            else
            {
                ConsoleTextBox.Text = text;
            }
        }

        private void CreateNewAccount(string accountName, string accountPrivateKey, string password)
        {
            string encryptedPrivateKey = string.Empty;
            if (accountPrivateKey.Length == 64)
            {
                var data = Encoding.Unicode.GetBytes(accountPrivateKey);
                byte[] encrypted = ProtectedData.Protect(data, Encoding.Unicode.GetBytes(password), DataProtectionScope.LocalMachine);
                encryptedPrivateKey = Convert.ToBase64String(encrypted);
            }
            Account newAccount = new Account
            {
                AccountName = AddAccountNameTextBox.Text,
                PrivateKey = encryptedPrivateKey,
                Inventory = CreateItemList(),
                LevelingSettings = CreateClassLevelingList()
            };
            currentAccounts.Add(newAccount);
            RefreshAccountBox();
        }

        public List<Account.Item> CreateItemList()
        {
            List<Account.Item> Inventory = new List<Account.Item>
            {
                new Account.Item()
                {
                    TokenName = "DFKRGWD",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKRCKRT",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKRDLF",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKDRKWD",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKAMBRTFY",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKGLDVN",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSWFTHSL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKBLOATER",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKIRONSCALE",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLANTERNEYE",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKREDGILL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSILVERFIN",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSAILFISH",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSHIMMERSKIN",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKBLUESTEM",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSPIDRFRT",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKMILKWEED",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKGREGG",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKBLUEEGG",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKGREENEGG",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKYELOWEGG",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLMGHTCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLSWFTCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLFRTICR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLINSCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLFINCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLVGRCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLWITCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKLFRTUCR",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKGOLD",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKTEARS",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSHVAS",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                 new Account.Item()
                {
                    TokenName = "DFKMOKSHA",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "JEWEL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "ONE",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKFROSTDRUM",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKKNAPROOT",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSHAGGYCAPS",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSKUNKSHADE",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKFROSTBLOATER",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKSPECKLETAIL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKKINGPINCER",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "DFKTHREEEYEDEEL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "CRYSTAL",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "SDGAS",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
                new Account.Item()
                {
                    TokenName = "CVGAS",
                    AutoSell = false,
                    AutoTransfer = "",
                    MinQuantityLeft = 0,
                    MinSellAmount = 1
                },
            };
            return Inventory;
        }
        public List<Account.ClassLevelingSettings> CreateClassLevelingList()
        {
            List<Account.ClassLevelingSettings> ClassLevelingSettingsList = new List<Account.ClassLevelingSettings>()
            {
                new Account.ClassLevelingSettings
                {
                    Class = "KNIGHT",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,END,STR",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "WARRIOR",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,DEX,STR",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "ARCHER",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "DEX,AGI,LCK",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "THIEF",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "AGI,LCK,DEX",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "MONK",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,DEX,STR",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "PIRATE",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "STR,LCK,DEX",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "PRIEST",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "WIS,INT,AGI",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "WIZARD",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "INT,WIS,LCK",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "SEER",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "WIS,INT,LCK",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "BERSERKER",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "STR,VIT,LCK",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "PALADIN",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,END,WIS",

                },
                new Account.ClassLevelingSettings
                {
                    Class = "DARKKNIGHT",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,INT,STR",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "NINJA",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "AGI,LCK,DEX",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "SUMMONER",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "INT,WIS,LCK",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "SHAPESHIFTER",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "AGI,LCK,DEX",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "DRAGOON",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,DEX,STR",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "SAGE",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "WIS,INT,AGI",
                },
                new Account.ClassLevelingSettings
                {
                    Class = "DREADKNIGHT",
                    Enabled = true,
                    CombatLevelingStatEnabled = false,
                    ProfessionLevelingEnabled = true,
                    CombatLevelingStats = "VIT,LCK,STR",
                }
            };
            return ClassLevelingSettingsList;
        }

        #endregion
    }
}
