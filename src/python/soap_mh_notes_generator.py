import random
import time

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    """ One example: http://learn.chm.msu.edu/clinicalhpcases/content/psychiatry/Psychiatry_HP.pdf
    """

    """ Use of terminology: http://web.utah.edu/umed/courses/year3/psychiatry/psychaid.html#soon 
    """ 


    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%m/%d/%Y %I:%M %p', prop)

print randomDate("1/1/2008 1:30 PM", "1/1/2009 4:50 AM", random.random())

start_timestamp = time.mktime(time.strptime('Jun 1 2010  01:33:00', '%b %d %Y %I:%M:%S'))
end_timestamp = time.mktime(time.strptime('Jun 1 2017  12:33:00', '%b %d %Y %I:%M:%S'))

def randomize_time(start_timestamp,end_timestamp):
    return time.strftime('%b %d %Y %I:%M:%S', time.localtime(randrange(start_timestamp,end_timestamp)))


#############################  Templates ############################################

""" Translated from University of Chicago Psychiatry Clerkship, Pritzker School of Medicine, retrived 9/14/2015 """
header = "${date} and ${time}"

# S - Subjective section
# Choose these from the papers
subjective = "Subjective:${symptoms} ${course}"

collateral_information = "Collateral information" "Stresses"

#Staff reports some|no|frequent agitation, irregular|regular|poor sleep, general|great|no cooperativeness|great, 
# and overally good|poor|problematic|satisfactory behavior.

agitation = random.choice(["some","no","frequent"])
sleep_log = random.choice(["irregular","regular","poor"])
cooperativeness = random.choice(["generally","not","greatly"])
behavior = random.choice(["good","poor","problematic","satisfactory"])
staff_observations = "Staff observations: Patient is experiencing ${agitation} agitation, a sleep is ${sleep_log$}, \
patient is ${cooperation} cooperative, and the behavior is ${behavior}."

template.replace(staff_observations, agitation)


# TODO: research common medications and frequency
medications = "Medications" = ["${name, dose, route, frequency, duration, therapeutic and side effects, compliance}"]

# TODO: research other treatments and frequency
other_treatments = "Other treatments:" = "${ECT (treatment #, and as with medications)}$, ${psychotherapy}"

#This will be used as a static sub-header
objective = "Objective:"


appearance = "Appearance:" ="${gait ____}, ${posture ____}, ${clothes ____}, ${grooming} ,${mileage}"

general_behavior = "General behavior: mannerisms ____, gestures ____, psychomotor activity ____, expression ____,"+
",eye contact,able to follow commands/requests,compulsions"

#Write as Patient attitude is .... Include maybe more than one.
attitude = "Attitude is "," cooperative, "," hostile, "," defensive, "," open, "," secretive, "," evasive, "," suspicious, "," apathetic,"+
"easily distracted,focused, etc."

LOC = "LOC: "," vigilant, "," alert, "," drowsy, "," lethargic, "," stuporous, "," asleep, "," comatose, "," confused, "," fluctuating, etc."

attention = "Attention: "," can attend, "," can concentrate, "," distractible, "," digit span, "," DLROW, "," calculations"

orientation = "Orientation: "," person, "," place, "," time, "," situation"

memory = "Memory: "," immediate, "," recent, "," remote"

intellectual = "Intellectual: fund of knowledge ____, vocabulary ____"

MMSE = "MMSE: __ points out of 30 achieved, missing the following tasks ____"

#"The volume of the speach is ${volume_tone}, and the speech is ${rate}. Patient is ${amount}, and ${fluency_rhytm}. "
speech = "Speech: volume/tone (loud,soft,monotone,weak,strong), rate (fast,slow,normal,pressured),"+
"amount (talkative,spontaneous,expansive,paucity,poverty), fluency/rhythm (slurred,clear,"+
",with appropriately placed inflections, "," hesitant, "," with good articulation, "," aphasic)"

mood="The mood of the patient is ${mood}"
mood = "Mood (inquired): "," depressed, "," euthymic, "," elevated, "," euphoric, "," irritable, "," anxious, etc."
affect "The affect is ${affect}, ${fluctuations}, ${range}, ${intensity}, and ${quality}."
affect = "Affect (observed): "," appropriate to situation, "," consistent with mood, "," congruent with thought content,"+
"fluctuations (labile,even), range (broad,restricted), intensity (blunted,flat, normal),"+
"quality ("," sad, "," angry, "," hostile, "," indifferent, "," euthymic, "," dysphoric, "," detached, "," elated,"+
" euphoric, "," anxious, "," animated, "," irritable)"
thought_process ="Thought process is ${thought_process}."
thought_process = "Thought process/form: "," linear, "," goal-directed, "," circumstantial, "," tangential, "," loose associations,"+
",incoherent,evasive,racing,thought blocking,perseveration,neologisms"
thought_process ="Thought process is ${delusions}, ${suicide_homocide}, ${phobias}, ${obsessions}."
thought_content = "Thought content: "," delusions (type: "," paranoid/persecutory, "," grandiose, "," somatic, "," religious, "," bizarre,"+
"nihilistic,thought insertion, thought withdrawal, thought broadcasting), ideas of reference,"+
"magical thinking, illusions/hallucinations (type: auditory, visual, somatic, olfactory,"+
",gustatory, command, conversation, commentary), "," suicide/homicide (elaborate further:"+
",active,passive,hopelessness,plan,detailed plan,partially executed plan,method available,"+
",impulsivity,command hallucinations,intention,contracting), phobias (type:,social,"+
",agoraphobia,specific/simple),obsessions"

insight_judgment = "Insight/Judgement: TODO/CONTINUE"
insight_judgment = "Insight/Judgement: ${awareness_of_problems}","abstract (similarities, proverbs), ${facts_understand}" + 
",${drawing_conclusions}, ${problem_solving}."

lab_tests = "Laboratory & other tests"

assessment = "Assessment: ${working_primary_diagnosis}, ${current_differential_diagnosis}, ${other_diagnoses}."

""" Definition of axis: https://faculty.fortlewis.edu/burke_b/abnormal/abnormalmultiaxial.htm
    In DSM-V, there is only one axis.
"""
axis_I = "DSM-IV Axis I:{dsm_iv_axis_i}"
axis_II = "DSM-IV Axis II:{dsm_iv_axis_ii}"
axis_III = "DSM-IV Axis III:{dsm_iv_axis_iii}"
DSM_V_ axis = "DSM-V Axis: ${dsm_v_axis}"

plan = "Plan:"
diagnostic="Diagnostic: ${obtain_collateral_information}, ${further_observation}, ${questioning}, ${tests}, etc."
specific_treatment = "Specific treatment: based upon diagnosis, e.g., medication titration, how many more ECT sessions, etc."
general_treatment = "General treatment: ${stres_reduction}, ${environmental_modification}, ${symptomatic} (e.g., insomnia), ${education}"

disposition = "Disposition: next source of care, follow-up, back-up plans"
reporting_physician = "${md_name}, ${title} (e.g., MS3), ${pager_number}, ${signature}"