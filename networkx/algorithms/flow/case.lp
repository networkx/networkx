\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  edge_B_to_A + 2 edge_A_to_C + 2 edge_B_to_C + 3 edge_D_to_B
   + 4 edge_E_to_B + 3 edge_E_to_D + 4 edge_E_to_F + edge_C_to_E
   + 3 edge_D_to_F + edge_E_to_G + 2 edge_G_to_C
Subject To
 demand_constraint_on_node_0: edge_B_to_A - edge_A_to_C = -2
 demand_constraint_on_node_1: - edge_B_to_A - edge_B_to_C + edge_D_to_B
   + 1.5 edge_E_to_B = 0
 demand_constraint_on_node_2: edge_A_to_C + 0.75 edge_B_to_C - edge_C_to_E
   + edge_G_to_C = 0
 demand_constraint_on_node_3: - edge_D_to_B + edge_E_to_D - edge_D_to_F
   = 0
 demand_constraint_on_node_4: - edge_E_to_B - edge_E_to_D - edge_E_to_F
   + 0.9 edge_C_to_E - edge_E_to_G = 0
 demand_constraint_on_node_5: 1.5 edge_E_to_F + 0.8 edge_D_to_F = 0
 demand_constraint_on_node_6: edge_E_to_G - edge_G_to_C = 2
Bounds
 edge_B_to_A <= 5
 edge_A_to_C <= 4
 edge_B_to_C <= 5
 edge_D_to_B <= 4
 edge_E_to_B <= 4
 edge_E_to_D <= 4
 edge_E_to_F <= 4
 edge_C_to_E <= 4
 edge_D_to_F <= 5
 edge_E_to_G <= 4
 edge_G_to_C <= 4
End
