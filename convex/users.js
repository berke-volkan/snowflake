import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// Mutation to store arbitrary key/value pairs for a user.
// We accept an array of { key, value } objects to avoid strict object-shape validation
// issues when keys vary between users. Each call inserts a new record associating
// `userId` with the provided info object. If you need true upsert semantics (one
// canonical row per userId) we can add a query/index and patch the existing row.
export const createUser = mutation({
  args: {
    userId: v.string(),
    fields: v.optional(v.array(v.object({ key: v.string(), value: v.string() }))),
     keys: v.array(v.object({ name: v.string(), token: v.bytes() })),
  },
  handler: async (ctx, args) => {
    const info = {};

    const id = await ctx.db.insert("users", { userId: args.userId, keys: args.keys });
    return id;
  },
});

export const updateUserKeys = mutation({
  args: {
    userId: v.string(),
    fields: v.optional(v.array(v.object({ key: v.string(), value: v.string() }))),
     keys: v.array(v.object({ name: v.string(), token: v.bytes() })),
  },
  handler: async (ctx, args) => {
    const info = {};
    const results = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("userId"), args.userId))
      .collect();
    const id = await ctx.db.patch(results[0]._id, { userId: args.userId, keys: args.keys });
    return id;
  },
});

export const getUserInfo = query({
  args: { userId: v.string(),},
  handler: async (ctx, args) => {
    const results = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("userId"), args.userId))
      .collect();
    return results;
  },
});

