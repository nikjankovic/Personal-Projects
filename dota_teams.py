# Import libraries
import pandas as pd

file_path = "./DotaHeroesDB.xlsx"

# Retrieve heroes data from database
dota_df_raw = pd.read_excel(file_path)
dota_df = dota_df_raw.dropna(how='all') # remove rows with NaN

# Dictionary to store hero attributes
hero_dict = dict(zip(dota_df["Hero Name"], dota_df["Role"]))

# Create dataframe from pairwise matrix (opposition)
relative_strength_matrix_df = pd.read_excel(file_path, sheet_name = "Relative Strength")

# Create dataframe from pairwise matrix (complimentary)
complimentary_matrix_df = pd.read_excel(file_path, sheet_name = "Complimentary Heroes")

relative_strength_matrix_df

def delete_row(team, df):
  """
  Returns df with selected heroes row removed.

  team: list of strings
  df: pandas dataframe
  """
  for hero in team:
    df = df[df.Heroes != hero]
  return df



def check_name(team):
  """
  Returns True if all hero in the team exists. False otherwise.

  team: list of str heroes
  """
  for hero in team:
    if hero not in hero_dict:
      return False
  return True



def format_input(heroes):
  """
  Returns a list of strings.

  heroes: string of player 1's hero selections
  """
  return [hero.strip().title() for hero in heroes.split(",")]



def update_team(team, new_heroes, df):
  """
  Returns updated team with added heroes and updated df.

  team: list of strings
  new: player 's hero selections in current round
  df: pandas dataframe of heroes' relative strength to each other
  """
  team.extend(new_heroes) # add additional hero selection to team
  df = delete_row(new_heroes, df) # kick team out
  return team, df



def print_teams(p1_team, p2_team):
  print("p1_team: ", p1_team)
  print("p2_team: ", p2_team)



# DATAFRAME HELPER FUNCTIONS --------------------------------------------------



def sum_columns(df, column_list):
  """
  Returns a filtered dataframe of summed columns

  df: pandas dataframe
  column_list: list of column names
  """
  df['Summed'] = 0

  for column in column_list:
    df['Summed'] += df[column]

  return df.filter(['Heroes', 'Summed'])



def sort_column(df, column_name):
  """
  Returns dataframe sorted in descending order of values.

  df: pandas dataframe
  column_list: list of column names
  """
  return df.sort_values(column_name, ascending=False)



def get_sorted_sum(df, column_list):
  """
  Returns dataframe sorted in descending order of summed values

  df: pandas dataframe
  column_list: list of column names
  """
  df = sum_columns(df, column_list)
  df = sort_column(df, column_list)
  return df



# -----------------------------------------------------------------------------



# Criteria 1: Unique role within team
def check_role(hero, team):
  """
  Check whether hero role is present in team. Return True if role is exists; False otherwise.

  hero: name (str)
  team: list of strings
  """
  role = hero_dict[hero]
  if role in team.values():  # ..and check whether its role is different to hero roles already selected for p2 before adding
    return True
  return False



# Criteria 2: Relative strength of heroes against another
def sum_hero_strength(team, df, p2_team = [], df2 = False):
  #TODO: Ensure hero rows are in the same order across the two dfs
  """
  Returns a player 1's team after inputting hero names and updated df.

  team: list of strings
  new: player 's hero selections in current round
  df: pandas dataframe of heroes' relative strength to each other
  """
  df['Summed'] = 0 # instantiate an empty column

  for hero in team: # for each hero in p1's team..
    df['Summed'] += df[hero] # ..sum the relative strengths of all heroes
  if df2 is not False:
    for hero in p2_team: # for each hero in p2's team..
      df['Summed'] += df2[hero] # ..sum the complimentary strengths of all heroes

  df = df.sort_values('Summed', ascending=False) # sort column in descending order
  return df



def suggest_heroes(p1_team, p2_team, df, df2, limit):
  """
  Returns dict of all suggested heroes for p2's team.
  """
  while len(p2_team) < limit:
    suggested_hero = df['Heroes']
    sub_df = df[['Role', 'Summed']].values.tolist()
    suggested = dict(zip(df['Heroes'], sub_df))

    #print(p2_team)

    # role check: ensure suggested list has no heroes with the same roles already chosen for player 2
    for i in suggested_hero:

      # list of roles existing in p2 team
      taken_roles = []
      for characteristics in p2_team.values():
        if type(characteristics) == list:
          taken_roles.append(characteristics[0])
        else:
          taken_roles.append(characteristics)

      if hero_dict[i] in taken_roles:
        del suggested[i]


    print(suggested)
    print("-----------------------------------")

    j = input("Enter a hero to be added into player 2's team: ").title().strip()

    if j in suggested.keys():
      p2_team[j] = suggested[j][0] # add hero roles only; not relative strength
      df = sum_hero_strength(p1_team, df, p2_team, df2)
    else:
      print("Invalid hero. Please retry.")

  return p2_team



def select_team(p1_team, p2_team, df, limit, df2=False):
  if limit == 2:
    # first selection round; p1 has selected 0 heroes & p2 has selected 0 heroes
    p1_team_user_input = input("Enter player 1's first hero: ")
  elif limit == 4:
    # second selection round; p1 has selected 1 heroes & p2 has selected 2 heroes
    p1_team_user_input = input("Enter player 1's second and third hero separated by a comma (','): ")
  else:
    # third selection round; p1 has selected 3 heroes & p2 has selected 4 heroes
    p1_team_user_input = input("Enter player 1's fourth and fifth hero separated by a comma (','): ")

  p1_new = format_input(p1_team_user_input)

  # checks user input against df
  if not check_name(p1_new):
    print("Invalid hero name in player 1's team. Please retry.")
    p1_team, p2_team, df = select_team(p1_team, p2_team, df, limit)
  elif limit == 2 and len(p1_new) != 1:
    print("Invalid number of heroes. Please retry.")
    p1_team, p2_team, df = select_team(p1_team, p2_team, df, limit)
  elif limit != 2 and len(p1_new) != 2:
    print("Invalid number of heroes. Please retry.")
    p1_team, p2_team, df = select_team(p1_team, p2_team, df, limit)
  else:
    if limit == 2:
      p1_team, df = update_team(p1_new, [], df)
    else:
      p1_team, df = update_team(p1_team, p1_new, df)

    df = sum_hero_strength(p1_team, df, p2_team, df2)
    p2_team = suggest_heroes(p1_team, p2_team, df, df2, limit)
    df = delete_row(p2_team.keys(), df) # kick p2_team out

    print_teams(p1_team, p2_team)
    print("-----------------------------------")

  return p1_team, p2_team, df



def main():
  relative_strength_matrix_df = pd.read_excel(file_path, sheet_name = "Relative Strength")
  complimentary_matrix_df = pd.read_excel(file_path, sheet_name = "Complimentary Heroes")
  # first selection round; p1 has selected no heroes
  p1_team, p2_team, relative_strength_matrix_df = select_team([], {}, relative_strength_matrix_df, 2, complimentary_matrix_df)
  # second selection round; p1 has selected 1 heroes & p2 has selected 2 heroes
  p1_team, p2_team, relative_strength_matrix_df = select_team(p1_team, p2_team, relative_strength_matrix_df, 4, complimentary_matrix_df)
  # third selection round; p1 has selected 3 heroes & p2 has selected 4 heroes
  p1_team, p2_team, relative_strength_matrix_df = select_team(p1_team, p2_team, relative_strength_matrix_df, 5, complimentary_matrix_df)



main()