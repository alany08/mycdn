from fractions import Fraction
from time import time

"""
matrix = [
	[1, 0, -3, 6],
	[4, 4, 3, 21],
        [0, 2, 5, 1]
]
"""
matrix = []
while True:
    row = input("Enter row (enter to finish): ")
    if not row:
        break
    row = row.split(",")
    for i in range(len(row)):
        row[i] = eval(row[i])
    matrix.append(row)

def print_matrix(matrix):
	for row in matrix:
		for col in row:
			print(Fraction(col).limit_denominator(), end="\t")
		print("")
	print("")
    input("")

#matrix operations

def swap_rows(matrix, r1, r2):
	matrix[r1], matrix[r2] = matrix[r2], matrix[r1]
	print("swap rows:", str(r1) + ",", r2)
	print_matrix(matrix)
	return matrix

def add_row(r1, r2):
	result_row = []
	for i in range(len(r1)):
		result_row.append(r1[i] + r2[i])

	return result_row

def add_row_to(matrix, r1, r2, r3): # r1 + r2 -> r3
	matrix[r3] = add_row(matrix[r1], matrix[r2])
	print("add rows:", r1, "+", r2, "->", r3)
	print_matrix(matrix)
	return matrix

def subtract_row(r1, r2):
	result_row = []
	for i in range(len(r1)):
		result_row.append(r1[i] - r2[i])

	return result_row

def subtract_row_to(matrix, r1, r2, r3): # r1 - r2 -> r3
	matrix[r3] = subtract_row(matrix[r1], matrix[r2])
	print("subtract rows:", r1, "-", r2, "->", r3)
	print_matrix(matrix)
	return matrix

def scale_row(r, scale):
	result_row = []
	for val in r:
		result_row.append(val * scale)

	return result_row

def scale_row_matrix(matrix, r, scale):
	matrix[r] = scale_row(matrix[r], scale)
	print("scale row:", r, "by", Fraction(scale).limit_denominator())
	print_matrix(matrix)
	return matrix

def sort_by_first_col(matrix):
	first_col = [row[0] for row in matrix]
	sorted_first_col = sorted(first_col)
	sorted_first_col.reverse()

	while first_col != sorted_first_col:
		for i in range(len(matrix)):
			for j in range(i):
				if matrix[i][0] > matrix[j][0]:
					matrix = swap_rows(matrix, i, j)

		first_col = [row[0] for row in matrix]

	print("sort matrix by first col")
	print_matrix(matrix)
	return matrix

def write_row(matrix, row, row_num):
	matrix[row_num] = row
	print("write", row, "to", row_num)
	print_matrix(matrix)
	return matrix

def shift_zeroes_to_bottom(matrix):
	for i in range(len(matrix)):
		zero = True
		row = matrix[i]
		for col in row:
			if col != 0:
				zero = False
		if zero and i != len(matrix) - 1:
			swap_rows(matrix, i, len(matrix) - 1)

	print("shift all zero rows to bottom")
	print_matrix(matrix)
	return matrix

#ACTUAL CALC START
start_time = time()

# check for multiple zeroes later
matrix = sort_by_first_col(matrix)

print("MATRIX SORTED\n")

#shift zeroes to the bottom
matrix = shift_zeroes_to_bottom(matrix)

print("ALL ZEROES SHIFTED TO BOTTOM\n")

#row echelon form
for row in range(len(matrix)):
	if matrix[row][row] == 0: continue

	matrix = scale_row_matrix(matrix, row, 1/matrix[row][row])

	for row_below in range(row+1, len(matrix)):
		row_below_val = matrix[row_below][row]
		if row_below_val == 0: continue

		matrix = scale_row_matrix(matrix, row, row_below_val)
		matrix = subtract_row_to(matrix, row_below, row, row_below)
		matrix = scale_row_matrix(matrix, row, 1/row_below_val)

print("ROW ECHELON FORM ACHIEVED\n")
	
#reduced row echelon form
for row in range(len(matrix)):
	for row_above in range(row):
		if matrix[row_above][row] == 0: continue
		row_above_val = matrix[row_above][row]
		if row_above_val == 0: continue

		matrix = scale_row_matrix(matrix, row, row_above_val)
		matrix = subtract_row_to(matrix, row_above, row, row_above)
		matrix = scale_row_matrix(matrix, row, 1/row_above_val)

#shift zeroes to the bottom
matrix = shift_zeroes_to_bottom(matrix)

print("REDUCED ROW ECHELON FORM ACHIEVED\n")

end_time = time()

print("Execution time:", (end_time - start_time)*1000, "ms")
