/*
**	Command & Conquer Generals Zero Hour(tm)
**	Copyright 2025 Electronic Arts Inc.
**
**	This program is free software: you can redistribute it and/or modify
**	it under the terms of the GNU General Public License as published by
**	the Free Software Foundation, either version 3 of the License, or
**	(at your option) any later version.
**
**	This program is distributed in the hope that it will be useful,
**	but WITHOUT ANY WARRANTY; without even the implied warranty of
**	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
**	GNU General Public License for more details.
**
**	You should have received a copy of the GNU General Public License
**	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

////////////////////////////////////////////////////////////////////////////////
//																																						//
//  (c) 2001-2003 Electronic Arts Inc.																				//
//																																						//
////////////////////////////////////////////////////////////////////////////////

// FILE: Diplomacy.cpp ///////////////////////////////////////////////////////////////////////
// Author: Matthew D. Campbell - August 2002
// Desc: GUI callbacks for the diplomacy menu
///////////////////////////////////////////////////////////////////////////////////////////////////

// INCLUDES ///////////////////////////////////////////////////////////////////////////////////////
#include "PreRTS.h"	// This must go first in EVERY cpp file in the GameEngine

#include "Common/GlobalData.h"
#include "Common/MultiplayerSettings.h"
#include "Common/MessageStream.h"
#include "Common/Money.h"
#include "Common/Player.h"
#include "Common/PlayerList.h"
#include "Common/PlayerTemplate.h"
#include "Common/Recorder.h"
#include "GameClient/AnimateWindowManager.h"
#include "GameClient/Diplomacy.h"
#include "GameClient/DisconnectMenu.h"
#include "GameClient/GameWindow.h"
#include "GameClient/GameWindowManager.h"
#include "GameClient/Gadget.h"
#include "GameClient/GadgetCheckBox.h"
#include "GameClient/GadgetListBox.h"
#include "GameClient/GadgetTextEntry.h"
#include "GameClient/GadgetStaticText.h"
#include "GameClient/GadgetRadioButton.h"
#include "GameClient/GameClient.h"
#include "GameClient/GameFont.h"
#include "GameClient/GameText.h"
#include "GameClient/GUICallbacks.h"
#include "GameClient/InGameUI.h"
#include "GameClient/WinInstanceData.h"
#include "GameLogic/GameLogic.h"
#include "GameLogic/Object.h"
#include "GameLogic/Module/ContainModule.h"
#include "GameLogic/VictoryConditions.h"
#include "GameNetwork/GameInfo.h"
#include "GameNetwork/NetworkInterface.h"
#include "GameNetwork/GameSpy/BuddyDefs.h"
#include "GameNetwork/GameSpy/PeerDefs.h"


//-------------------------------------------------------------------------------------------------

static NameKeyType staticTextPlayerID[MAX_SLOTS];
static NameKeyType staticTextSideID[MAX_SLOTS];
static NameKeyType staticTextTeamID[MAX_SLOTS];
static NameKeyType staticTextStatusID[MAX_SLOTS];
static NameKeyType buttonMuteID[MAX_SLOTS];
static NameKeyType buttonUnMuteID[MAX_SLOTS];
enum { RESOURCE_TRANSFER_AMOUNT_COUNT = 3 };
static const UnsignedInt resourceTransferAmounts[RESOURCE_TRANSFER_AMOUNT_COUNT] = { 500, 1000, 5000 };
static const char *resourceTransferLabels[RESOURCE_TRANSFER_AMOUNT_COUNT] = { "$500", "$1K", "$5K" };
static NameKeyType buttonTransferID[MAX_SLOTS][RESOURCE_TRANSFER_AMOUNT_COUNT];
static NameKeyType buttonTransferBuildingID[MAX_SLOTS];
static NameKeyType radioButtonInGameID = NAMEKEY_INVALID;
static NameKeyType radioButtonBuddiesID = NAMEKEY_INVALID;
static GameWindow *radioButtonInGame = nullptr;
static GameWindow *radioButtonBuddies = nullptr;
static NameKeyType winInGameID = NAMEKEY_INVALID;
static NameKeyType winBuddiesID = NAMEKEY_INVALID;
static NameKeyType winSoloID = NAMEKEY_INVALID;
static GameWindow *winInGame = nullptr;
static GameWindow *winBuddies = nullptr;
static GameWindow *winSolo = nullptr;
static GameWindow *staticTextPlayer[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *staticTextSide[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *staticTextTeam[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *staticTextStatus[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *buttonMute[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *buttonUnMute[MAX_SLOTS] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};
static GameWindow *buttonTransfer[MAX_SLOTS][RESOURCE_TRANSFER_AMOUNT_COUNT] = {};
static GameWindow *buttonTransferBuilding[MAX_SLOTS] = {};
static Int slotNumInRow[MAX_SLOTS];

//-------------------------------------------------------------------------------------------------

static WindowLayout *theLayout = nullptr;
static GameWindow *theWindow = nullptr;
static AnimateWindowManager *theAnimateWindowManager = nullptr;
WindowMsgHandledType BuddyControlSystem( GameWindow *window, UnsignedInt msg,
														 WindowMsgData mData1, WindowMsgData mData2);
void InitBuddyControls(Int type);
void updateBuddyInfo();
static void updateResourceTransferButtons();
static void grabWindowPointers()
{
	for (Int i=0; i<MAX_SLOTS; ++i)
	{
		AsciiString temp;
		temp.format("Diplomacy.wnd:StaticTextPlayer%d", i);
		staticTextPlayerID[i] = NAMEKEY(temp);
		temp.format("Diplomacy.wnd:StaticTextSide%d", i);
		staticTextSideID[i] = NAMEKEY(temp);
		temp.format("Diplomacy.wnd:StaticTextTeam%d", i);
		staticTextTeamID[i] = NAMEKEY(temp);
		temp.format("Diplomacy.wnd:StaticTextStatus%d", i);
		staticTextStatusID[i] = NAMEKEY(temp);
		temp.format("Diplomacy.wnd:ButtonMute%d", i);
		buttonMuteID[i] = NAMEKEY(temp);
		temp.format("Diplomacy.wnd:ButtonUnMute%d", i);
		buttonUnMuteID[i] = NAMEKEY(temp);

		staticTextPlayer[i] = TheWindowManager->winGetWindowFromId(theWindow, staticTextPlayerID[i]);
		staticTextSide[i] = TheWindowManager->winGetWindowFromId(theWindow, staticTextSideID[i]);
		staticTextTeam[i] = TheWindowManager->winGetWindowFromId(theWindow, staticTextTeamID[i]);
		staticTextStatus[i] = TheWindowManager->winGetWindowFromId(theWindow, staticTextStatusID[i]);
		buttonMute[i] = TheWindowManager->winGetWindowFromId(theWindow, buttonMuteID[i]);
		buttonUnMute[i] = TheWindowManager->winGetWindowFromId(theWindow, buttonUnMuteID[i]);
		for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
		{
			temp.format("Diplomacy.wnd:ButtonTransfer%d_%d", i, amountIndex);
			buttonTransferID[i][amountIndex] = NAMEKEY(temp);
			buttonTransfer[i][amountIndex] = TheWindowManager->winGetWindowFromId(theWindow, buttonTransferID[i][amountIndex]);
		}
		temp.format("Diplomacy.wnd:ButtonTransferBuilding%d", i);
		buttonTransferBuildingID[i] = NAMEKEY(temp);
		buttonTransferBuilding[i] = TheWindowManager->winGetWindowFromId(theWindow, buttonTransferBuildingID[i]);

		slotNumInRow[i] = -1;
	}
}

static void releaseWindowPointers()
{
	for (Int i=0; i<MAX_SLOTS; ++i)
	{
		staticTextPlayer[i] = nullptr;
		staticTextSide[i] = nullptr;
		staticTextTeam[i] = nullptr;
		staticTextStatus[i] = nullptr;
		buttonMute[i] = nullptr;
		buttonUnMute[i] = nullptr;
		for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
			buttonTransfer[i][amountIndex] = nullptr;
		buttonTransferBuilding[i] = nullptr;

		slotNumInRow[i] = -1;
	}
}

//-------------------------------------------------------------------------------------------------
static void createResourceTransferButtons()
{
	if (!TheGlobalData || !TheGlobalData->m_sharedControl)
		return;

	for (Int row = 0; row < MAX_SLOTS; ++row)
	{
		if (!staticTextStatus[row] || buttonTransfer[row][0])
			continue;

		GameWindow *parent = staticTextStatus[row]->winGetParent();
		Int x = 0, y = 0, width = 0, height = 0;
		staticTextStatus[row]->winGetPosition(&x, &y);
		staticTextStatus[row]->winGetSize(&width, &height);
		const Int gap = 2;
		const Int buttonWidth = (width - gap * (RESOURCE_TRANSFER_AMOUNT_COUNT - 1)) / RESOURCE_TRANSFER_AMOUNT_COUNT;

		for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
		{
			WinInstanceData instData;
			instData.init();
			instData.m_id = buttonTransferID[row][amountIndex];
			BitSet(instData.m_style, GWS_PUSH_BUTTON | GWS_MOUSE_TRACK);
			instData.m_textLabelString = resourceTransferLabels[amountIndex];
			UnicodeString tooltip;
			tooltip.format(L"Send $%u to this ally", resourceTransferAmounts[amountIndex]);
			instData.setTooltipText(tooltip);

			buttonTransfer[row][amountIndex] = TheWindowManager->gogoGadgetPushButton(
				parent, WIN_STATUS_ENABLED,
				x + amountIndex * (buttonWidth + gap), y, buttonWidth, height,
				&instData, staticTextStatus[row]->winGetFont(), TRUE);
			if (buttonTransfer[row][amountIndex])
			{
				buttonTransfer[row][amountIndex]->winSetOwner(theWindow);
				buttonTransfer[row][amountIndex]->winHide(TRUE);
			}
		}

		WinInstanceData buildingData;
		buildingData.init();
		buildingData.m_id = buttonTransferBuildingID[row];
		BitSet(buildingData.m_style, GWS_PUSH_BUTTON | GWS_MOUSE_TRACK);
		buildingData.m_textLabelString = "TRANSFER BLDG";
		buildingData.setTooltipText(L"Transfer the selected supported building to this ally");
		GameFont *buildingButtonFont = staticTextStatus[row]->winGetFont();
		if (buildingButtonFont && TheFontLibrary)
		{
			const Int smallerPointSize = max(8, buildingButtonFont->pointSize * 2 / 3);
			buildingButtonFont = TheFontLibrary->getFont(
				buildingButtonFont->nameString, smallerPointSize, buildingButtonFont->bold);
		}
		buttonTransferBuilding[row] = TheWindowManager->gogoGadgetPushButton(
			parent, WIN_STATUS_ENABLED,
			x, y, width, height,
			&buildingData, buildingButtonFont, TRUE);
		if (buttonTransferBuilding[row])
		{
			buttonTransferBuilding[row]->winSetOwner(theWindow);
			buttonTransferBuilding[row]->winHide(TRUE);
		}
	}
}

//-------------------------------------------------------------------------------------------------
static Player *getPlayerForDiplomacyRow(Int row)
{
	if (!ThePlayerList || row < 0 || row >= MAX_SLOTS || slotNumInRow[row] < 0)
		return nullptr;

	AsciiString playerName;
	playerName.format("player%d", slotNumInRow[row]);
	return ThePlayerList->findPlayerWithNameKey(NAMEKEY(playerName));
}

//-------------------------------------------------------------------------------------------------
static Bool isSupportedAlliedTransferBuilding(Object *building)
{
	if (!building || !building->isKindOf(KINDOF_STRUCTURE))
		return false;

	const Bool isRiskyCategory = building->isKindOf(KINDOF_COMMANDCENTER)
		|| building->isKindOf(KINDOF_FS_SUPERWEAPON)
		|| building->isKindOf(KINDOF_FS_STRATEGY_CENTER)
		|| building->isKindOf(KINDOF_FS_INTERNET_CENTER)
		|| building->isKindOf(KINDOF_FS_ADVANCED_TECH)
		|| building->isKindOf(KINDOF_FS_AIRFIELD)
		|| building->isKindOf(KINDOF_FS_FAKE);
	ContainModuleInterface *contain = building->getContain();
	return !isRiskyCategory && (!contain || contain->getContainCount() == 0);
}

//-------------------------------------------------------------------------------------------------
static Object *getSelectedBuildingForTransfer()
{
	Player *localPlayer = ThePlayerList ? ThePlayerList->getLocalPlayer() : nullptr;
	if (!localPlayer || !TheInGameUI || TheInGameUI->getSelectCount() != 1)
		return nullptr;

	Drawable *draw = TheInGameUI->getFirstSelectedDrawable();
	Object *building = draw ? draw->getObject() : nullptr;
	if (!building || !building->isKindOf(KINDOF_STRUCTURE) || building->isEffectivelyDead()
			|| building->testStatus(OBJECT_STATUS_UNDER_CONSTRUCTION) || building->testStatus(OBJECT_STATUS_SOLD))
		return nullptr;

	Player *owner = building->getControllingPlayer();
	if (!owner || (owner != localPlayer && localPlayer->getRelationship(owner->getDefaultTeam()) != ALLIES))
		return nullptr;

	if (!isSupportedAlliedTransferBuilding(building))
		return nullptr;

	return building;
}

//-------------------------------------------------------------------------------------------------
static void updateResourceTransferButtons()
{
	Player *localPlayer = ThePlayerList ? ThePlayerList->getLocalPlayer() : nullptr;
	Object *selectedBuilding = getSelectedBuildingForTransfer();
	Player *buildingOwner = selectedBuilding ? selectedBuilding->getControllingPlayer() : nullptr;
	const Bool isBuildingTransferMode = selectedBuilding != nullptr;
	for (Int row = 0; row < MAX_SLOTS; ++row)
	{
		Player *recipient = getPlayerForDiplomacyRow(row);
		const Bool canTargetPlayer = TheGlobalData && TheGlobalData->m_sharedControl && localPlayer && recipient
			&& localPlayer->isPlayerActive() && recipient->isPlayerActive()
			&& !localPlayer->isPlayerObserver() && !recipient->isPlayerObserver()
			&& (localPlayer == recipient || localPlayer->getRelationship(recipient->getDefaultTeam()) == ALLIES);
		const Bool canTransferResources = !isBuildingTransferMode && canTargetPlayer && localPlayer != recipient;
		const Bool canTransferBuilding = canTargetPlayer && recipient->getPlayerType() == PLAYER_HUMAN
			&& selectedBuilding && buildingOwner && buildingOwner != recipient
			&& buildingOwner->getRelationship(recipient->getDefaultTeam()) == ALLIES;
		const Bool showBuildingButton = isBuildingTransferMode && canTargetPlayer && buildingOwner != recipient;

		if (staticTextStatus[row])
			staticTextStatus[row]->winHide(canTransferResources || showBuildingButton);

		for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
		{
			GameWindow *button = buttonTransfer[row][amountIndex];
			if (!button)
				continue;
			button->winHide(!canTransferResources);
			button->winEnable(canTransferResources && localPlayer->getMoney()->countMoney() >= resourceTransferAmounts[amountIndex]);
		}

		GameWindow *buildingButton = buttonTransferBuilding[row];
		if (buildingButton)
		{
			buildingButton->winHide(!showBuildingButton);
			buildingButton->winEnable(canTransferBuilding);
		}
	}
}


//-------------------------------------------------------------------------------------------------

static void updateFunc( WindowLayout *layout, void *param )
{
	updateResourceTransferButtons();
	if (theAnimateWindowManager && TheGlobalData->m_animateWindows)
	{
		Bool wasFinished = theAnimateWindowManager->isFinished();
		theAnimateWindowManager->update();
		if (theAnimateWindowManager->isFinished() && !wasFinished && theAnimateWindowManager->isReversed())
			theWindow->winHide( TRUE );
	}
}

//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
static BriefingList theBriefingList;

//-------------------------------------------------------------------------------------------------
BriefingList* GetBriefingTextList()
{
	return &theBriefingList;
}

//-------------------------------------------------------------------------------------------------
void UpdateDiplomacyBriefingText(AsciiString newText, Bool clear)
{
	GameWindow *listboxSolo = TheWindowManager->winGetWindowFromId(theWindow, NAMEKEY("Diplomacy.wnd:ListboxSolo"));

	if (clear)
	{
		theBriefingList.clear();
		if (listboxSolo)
			GadgetListBoxReset(listboxSolo);
	}

	if (newText.isEmpty())
		return;

	if (std::find(theBriefingList.begin(), theBriefingList.end(), newText) != theBriefingList.end())
		return;

	theBriefingList.push_back(newText);
	if (!listboxSolo)
		return;

	UnicodeString translated = TheGameText->fetch(newText);

	Int numEntries = GadgetListBoxGetNumEntries(listboxSolo);
	GadgetListBoxAddEntryText(listboxSolo, translated, TheInGameUI->getMessageColor(numEntries%2), -1);
}

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
void ShowDiplomacy( Bool immediate )
{
	if (!TheInGameUI->getInputEnabled() || TheGameLogic->isIntroMoviePlaying() ||
			TheGameLogic->isLoadingMap())
		return;


	if (TheInGameUI->isQuitMenuVisible())
		return;

	if (TheDisconnectMenu && TheDisconnectMenu->isScreenVisible())
		return;

	if (theWindow)
	{
		theWindow->winHide(FALSE);
		theWindow->winEnable(TRUE);
	}
	else
	{
		theLayout = TheWindowManager->winCreateLayout( "Diplomacy.wnd" );
		theWindow = theLayout->getFirstWindow();
		theLayout->setUpdate(updateFunc);
		theAnimateWindowManager = NEW AnimateWindowManager;
		radioButtonInGameID = TheNameKeyGenerator->nameToKey("Diplomacy.wnd:RadioButtonInGame");
		radioButtonBuddiesID = TheNameKeyGenerator->nameToKey("Diplomacy.wnd:RadioButtonBuddies");
		radioButtonInGame = TheWindowManager->winGetWindowFromId(nullptr, radioButtonInGameID);
		radioButtonBuddies = TheWindowManager->winGetWindowFromId(nullptr, radioButtonBuddiesID);
		winInGameID = TheNameKeyGenerator->nameToKey("Diplomacy.wnd:InGameParent");
		winBuddiesID = TheNameKeyGenerator->nameToKey("Diplomacy.wnd:BuddiesParent");
		winSoloID = TheNameKeyGenerator->nameToKey("Diplomacy.wnd:SoloParent");
		winInGame = TheWindowManager->winGetWindowFromId(nullptr, winInGameID);
		winBuddies = TheWindowManager->winGetWindowFromId(nullptr, winBuddiesID);
		winSolo = TheWindowManager->winGetWindowFromId(nullptr, winSoloID);

		if (!TheRecorder->isMultiplayer())
		{
			GameWindow *listboxSolo = TheWindowManager->winGetWindowFromId(theWindow, NAMEKEY("Diplomacy.wnd:ListboxSolo"));
			if (listboxSolo)
			{
				for (BriefingList::iterator it = theBriefingList.begin(); it != theBriefingList.end(); ++it)
				{
					UnicodeString translated = TheGameText->fetch(*it);
					Int numEntries = GadgetListBoxGetNumEntries(listboxSolo);
					GadgetListBoxAddEntryText(listboxSolo, translated, TheInGameUI->getMessageColor(numEntries%2), -1);
				}
			}
		}
	}
	theLayout->hide(FALSE);

	radioButtonInGame->winHide(TRUE);
	radioButtonBuddies->winHide(TRUE);
	GadgetRadioSetSelection(radioButtonInGame, FALSE);
	if (TheRecorder->isMultiplayer() || (TheGlobalData && TheGlobalData->m_sharedControl))
	{
		winInGame->winHide(FALSE);
		winBuddies->winHide(TRUE);
		winSolo->winHide(TRUE);
	}
	else
	{
		winInGame->winHide(TRUE);
		winBuddies->winHide(TRUE);
		winSolo->winHide(FALSE);
	}

	theAnimateWindowManager->reset();
	if (!immediate && TheGlobalData->m_animateWindows)
		theAnimateWindowManager->registerGameWindow( theWindow, WIN_ANIMATION_SLIDE_TOP, TRUE, 200 );

	TheInGameUI->registerWindowLayout(theLayout);
	grabWindowPointers();
	createResourceTransferButtons();
	PopulateInGameDiplomacyPopup();

	if(TheGameSpyInfo && TheGameSpyInfo->getLocalProfileID() != 0)
	{
		radioButtonInGame->winHide(FALSE);
		radioButtonBuddies->winHide(FALSE);
		InitBuddyControls(1);
		PopulateOldBuddyMessages();
		updateBuddyInfo();
	}

}

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
void ResetDiplomacy()
{
	if(theLayout)
	{
		TheInGameUI->unregisterWindowLayout(theLayout);
		theLayout->destroyWindows();
		deleteInstance(theLayout);
		InitBuddyControls(-1);
		theLayout = nullptr;
	}
	theWindow = nullptr;

	delete theAnimateWindowManager;
	theAnimateWindowManager = nullptr;
}

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
void HideDiplomacy( Bool immediate )
{
	releaseWindowPointers();
	if (theWindow)
	{
		if (immediate || !TheGlobalData->m_animateWindows)
		{
			theWindow->winHide(TRUE);
			theWindow->winEnable(FALSE);
		}
		else
		{
			if (theAnimateWindowManager->isFinished())
				theAnimateWindowManager->reverseAnimateWindow();
		}
	}
}

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
void ToggleDiplomacy( Bool immediate )
{
	// If we bring this up, let's hide the quit menu
	HideQuitMenu();

	if (theWindow)
	{
		Bool show = theWindow->winIsHidden();
		if (show)
			ShowDiplomacy( immediate );
		else
			HideDiplomacy( immediate );
	}
	else
	{
		ShowDiplomacy( immediate );
	}
}


//-------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------
WindowMsgHandledType DiplomacyInput( GameWindow *window, UnsignedInt msg,
																			WindowMsgData mData1, WindowMsgData mData2 )
{

	switch( msg )
	{

		// --------------------------------------------------------------------------------------------
		case GWM_CHAR:
		{
			UnsignedByte key = mData1;
//			UnsignedByte state = mData2;

			switch( key )
			{

				// ----------------------------------------------------------------------------------------
				case KEY_ESC:
				{
					HideDiplomacy();
					return MSG_HANDLED;
					//return MSG_IGNORED;
				}

			}

			return MSG_HANDLED;

		}

	}

	return MSG_IGNORED;

}

//-------------------------------------------------------------------------------------------------
WindowMsgHandledType DiplomacySystem( GameWindow *window, UnsignedInt msg,
																			 WindowMsgData mData1, WindowMsgData mData2 )
{
	if(BuddyControlSystem(window, msg, mData1, mData2) == MSG_HANDLED)
	{
		return MSG_HANDLED;
	}
	switch( msg )
	{
		//---------------------------------------------------------------------------------------------
		case GGM_FOCUS_CHANGE:
		{
//			Bool focus = (Bool) mData1;
			//if (focus)
				//TheWindowManager->winSetGrabWindow( chatTextEntry );
			break;
		}

		//---------------------------------------------------------------------------------------------
		case GWM_INPUT_FOCUS:
		{
			// if we're given the opportunity to take the keyboard focus we must say we don't want it
			if( mData1 == TRUE )
				*(Bool *)mData2 = FALSE;

			return MSG_HANDLED;
		}

		//---------------------------------------------------------------------------------------------
		case GBM_SELECTED:
		{
			GameWindow *control = (GameWindow *)mData1;
			NameKeyType controlID = (NameKeyType)control->winGetWindowId();
			static NameKeyType buttonHideID = NAMEKEY( "Diplomacy.wnd:ButtonHide" );
			if (controlID == buttonHideID)
			{
				HideDiplomacy( FALSE );
			}
			else if( controlID == radioButtonInGameID)
			{
				winInGame->winHide(FALSE);
				winBuddies->winHide(TRUE);
			}
			else if( controlID == radioButtonBuddiesID)
			{
				winInGame->winHide(TRUE);
				winBuddies->winHide(FALSE);
			}

			for (Int i=0; i<MAX_SLOTS; ++i)
			{
				if (controlID == buttonTransferBuildingID[i] && slotNumInRow[i] >= 0)
				{
					Player *recipient = getPlayerForDiplomacyRow(i);
					Object *building = getSelectedBuildingForTransfer();
					if (!recipient || !building)
						return MSG_HANDLED;
					GameMessage *transferMessage = TheMessageStream->appendMessage(GameMessage::MSG_TRANSFER_BUILDING);
					transferMessage->appendIntegerArgument(recipient->getPlayerIndex());
					transferMessage->appendObjectIDArgument(building->getID());
					return MSG_HANDLED;
				}
				for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
				{
					if (controlID == buttonTransferID[i][amountIndex] && slotNumInRow[i] >= 0)
					{
						Player *recipient = getPlayerForDiplomacyRow(i);
						if (!recipient)
							return MSG_HANDLED;
						GameMessage *transferMessage = TheMessageStream->appendMessage(GameMessage::MSG_TRANSFER_RESOURCES);
						transferMessage->appendIntegerArgument(recipient->getPlayerIndex());
						transferMessage->appendIntegerArgument(resourceTransferAmounts[amountIndex]);
						return MSG_HANDLED;
					}
				}
				if (controlID == buttonMuteID[i] && slotNumInRow[i] >= 0)
				{
					TheGameInfo->getSlot(slotNumInRow[i])->mute(TRUE);
					PopulateInGameDiplomacyPopup();
					break;
				}
				if (controlID == buttonUnMuteID[i] && slotNumInRow[i] >= 0)
				{
					TheGameInfo->getSlot(slotNumInRow[i])->mute(FALSE);
					PopulateInGameDiplomacyPopup();
					break;
				}
			}
			break;

		}

		//---------------------------------------------------------------------------------------------
		default:
			return MSG_IGNORED;

	}

	return MSG_HANDLED;

}

void PopulateInGameDiplomacyPopup()
{
	if (!TheGameInfo)
		return;

	Int rowNum = 0;
	for (Int slotNum=0; slotNum<MAX_SLOTS; ++slotNum)
	{
		const GameSlot *slot = TheGameInfo->getConstSlot(slotNum);
		if (slot && slot->isOccupied())
		{
			Bool isInGame = false;
			// Note - for skirmish, TheNetwork == nullptr.  jba.
			if (TheNetwork &&	TheNetwork->isPlayerConnected(slotNum)) {
				isInGame = true;
			} else if ((TheNetwork == nullptr) && slot->isHuman()) {
				// this is a skirmish game and it is the human player.
				isInGame = true;
			}
			if (slot->isAI())
				isInGame = true;
			AsciiString playerName;
			playerName.format("player%d", slotNum);
			Player *player = ThePlayerList->findPlayerWithNameKey(NAMEKEY(playerName));
			Bool isAlive = !TheVictoryConditions->hasSinglePlayerBeenDefeated(player);
			Bool isObserver = player->isPlayerObserver();

			if (slot->isHuman() && TheGameInfo->getLocalSlotNum() != slotNum && isInGame)
			{
				// show mute button
				if (buttonMute[rowNum])
				{
					buttonMute[rowNum]->winHide(slot->isMuted());
				}
				if (buttonUnMute[rowNum])
				{
					buttonUnMute[rowNum]->winHide(!slot->isMuted());
				}
			}
			else
			{
				// can't mute self, AI players, or MIA humans
				if (buttonMute[rowNum])
					buttonMute[rowNum]->winHide(TRUE);
				if (buttonUnMute[rowNum])
					buttonUnMute[rowNum]->winHide(TRUE);
			}

			Color playerColor = TheMultiplayerSettings->getColor(slot->getApparentColor())->getColor();
			Color backColor = GameMakeColor(0, 0, 0, 255);
			Color aliveColor = GameMakeColor(0, 255, 0, 255);
			Color deadColor = GameMakeColor(255, 0, 0, 255);
			Color observerInGameColor = GameMakeColor(255, 255, 255, 255);
			Color goneColor = GameMakeColor(196, 0, 0, 255);
			Color observerGoneColor = GameMakeColor(196, 196, 196, 255);

			if (staticTextPlayer[rowNum])
			{
				staticTextPlayer[rowNum]->winSetEnabledTextColors( playerColor, backColor );
				GadgetStaticTextSetText(staticTextPlayer[rowNum], slot->getName());
			}
			if (staticTextSide[rowNum])
			{
				staticTextSide[rowNum]->winSetEnabledTextColors( playerColor, backColor );
				GadgetStaticTextSetText(staticTextSide[rowNum], slot->getApparentPlayerTemplateDisplayName() );
			}
			if (staticTextTeam[rowNum])
			{
				staticTextTeam[rowNum]->winSetEnabledTextColors( playerColor, backColor );
				AsciiString teamStr;
				teamStr.format("Team:%d", slot->getTeamNumber() + 1);
				if (slot->isAI() && slot->getTeamNumber() == -1)
					teamStr = "Team:AI";
				GadgetStaticTextSetText(staticTextTeam[rowNum], TheGameText->fetch(teamStr) );
			}
			if (staticTextStatus[rowNum])
			{
				staticTextStatus[rowNum]->winHide(FALSE);
				if (isInGame)
				{
					if (isAlive)
					{
						staticTextStatus[rowNum]->winSetEnabledTextColors( aliveColor, backColor );
						GadgetStaticTextSetText(staticTextStatus[rowNum], TheGameText->fetch("GUI:PlayerAlive"));
					}
					else
					{
						if (isObserver)
						{
							staticTextStatus[rowNum]->winSetEnabledTextColors( observerInGameColor, backColor );
							GadgetStaticTextSetText(staticTextStatus[rowNum], TheGameText->fetch("GUI:PlayerObserver"));
						}
						else
						{
							staticTextStatus[rowNum]->winSetEnabledTextColors( deadColor, backColor );
							GadgetStaticTextSetText(staticTextStatus[rowNum], TheGameText->fetch("GUI:PlayerDead"));
						}
					}
				}
				else
				{
					// not in game
					if (isObserver)
					{
						staticTextStatus[rowNum]->winSetEnabledTextColors( observerGoneColor, backColor );
						GadgetStaticTextSetText(staticTextStatus[rowNum], TheGameText->fetch("GUI:PlayerObserverGone"));
					}
					else
					{
						staticTextStatus[rowNum]->winSetEnabledTextColors( goneColor, backColor );
						GadgetStaticTextSetText(staticTextStatus[rowNum], TheGameText->fetch("GUI:PlayerGone"));
					}
				}
			}

			slotNumInRow[rowNum++] = slotNum;
		}
	}

	while (rowNum < MAX_SLOTS)
	{
		slotNumInRow[rowNum] = -1;
		if (staticTextPlayer[rowNum])
			staticTextPlayer[rowNum]->winHide(TRUE);
		if (staticTextSide[rowNum])
			staticTextSide[rowNum]->winHide(TRUE);
		if (staticTextTeam[rowNum])
			staticTextTeam[rowNum]->winHide(TRUE);
		if (staticTextStatus[rowNum])
			staticTextStatus[rowNum]->winHide(TRUE);
		if (buttonMute[rowNum])
			buttonMute[rowNum]->winHide(TRUE);
		if (buttonUnMute[rowNum])
			buttonUnMute[rowNum]->winHide(TRUE);
		if (buttonTransferBuilding[rowNum])
			buttonTransferBuilding[rowNum]->winHide(TRUE);
		for (Int amountIndex = 0; amountIndex < RESOURCE_TRANSFER_AMOUNT_COUNT; ++amountIndex)
		{
			if (buttonTransfer[rowNum][amountIndex])
				buttonTransfer[rowNum][amountIndex]->winHide(TRUE);
		}

		++rowNum;
	}

	updateResourceTransferButtons();
}



